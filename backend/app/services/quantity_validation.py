from backend.app.models.entities import Organization, TeaGarden, GreenLeafLot, BatchEdge
from sqlalchemy.orm import Session

from backend.app.models.entities import (
    GreenLeafLot,
    FactoryBatch,
    WarehouseLot,
    AuctionLot,
    BlendBatch,
    PackageBatch,
    BatchEdge,
)


QUANTITY_FIELDS = {
    "GREEN_LEAF_LOT": "quantity_kg",
    "FACTORY_BATCH": "output_quantity_kg",
    "WAREHOUSE_LOT": "quantity_kg",
    "AUCTION_LOT": "quantity_kg",
    "BLEND_BATCH": "output_quantity_kg",
    "PACKAGE_BATCH": "quantity_kg",
}


MODEL_MAP = {
    "GREEN_LEAF_LOT": GreenLeafLot,
    "FACTORY_BATCH": FactoryBatch,
    "WAREHOUSE_LOT": WarehouseLot,
    "AUCTION_LOT": AuctionLot,
    "BLEND_BATCH": BlendBatch,
    "PACKAGE_BATCH": PackageBatch,
}


def get_entity_quantity(
    db: Session,
    entity_type: str,
    entity_id: int
):
    model = MODEL_MAP.get(entity_type)

    if not model:
        return None

    entity = (
        db.query(model)
        .filter(model.id == entity_id)
        .first()
    )

    if not entity:
        return None

    field_name = QUANTITY_FIELDS[entity_type]

    return getattr(entity, field_name, None)


def validate_source_allocation(
    db: Session,
    entity_type: str,
    entity_id: int
):
    source_quantity = get_entity_quantity(
        db,
        entity_type,
        entity_id
    )

    if source_quantity is None:
        return {
            "valid": False,
            "entity_type": entity_type,
            "entity_id": entity_id,
            "reason": "Source entity or quantity not found",
        }

    edges = (
        db.query(BatchEdge)
        .filter(
            BatchEdge.source_type == entity_type,
            BatchEdge.source_id == entity_id
        )
        .all()
    )

    allocated_quantity = 0.0
    invalid_edges = []

    for edge in edges:

        quantity = edge.quantity_kg

        if quantity is None:
            continue

        if quantity < 0:
            invalid_edges.append({
                "edge_id": edge.id,
                "reason": "Negative quantity",
                "quantity_kg": quantity,
            })
            continue

        allocated_quantity += quantity

    remaining_quantity = (
        source_quantity - allocated_quantity
    )

    return {
        "valid": (
            len(invalid_edges) == 0
            and allocated_quantity <= source_quantity
        ),
        "entity_type": entity_type,
        "entity_id": entity_id,
        "source_quantity_kg": source_quantity,
        "allocated_quantity_kg": allocated_quantity,
        "remaining_quantity_kg": remaining_quantity,
        "edge_count": len(edges),
        "invalid_edges": invalid_edges,
    }


def validate_blend_quantity(
    db: Session,
    blend_id: int
):
    blend = (
        db.query(BlendBatch)
        .filter(BlendBatch.id == blend_id)
        .first()
    )

    if not blend:
        return {
            "valid": False,
            "reason": "Blend batch not found",
        }

    edges = (
        db.query(BatchEdge)
        .filter(
            BatchEdge.target_type == "BLEND_BATCH",
            BatchEdge.target_id == blend_id,
            BatchEdge.relationship_type == "BLENDED_INTO",
        )
        .all()
    )

    input_quantity = sum(
        edge.quantity_kg or 0
        for edge in edges
    )

    output_quantity = (
        blend.output_quantity_kg or 0
    )

    return {
        "valid": input_quantity >= output_quantity,
        "blend_id": blend_id,
        "input_quantity_kg": input_quantity,
        "output_quantity_kg": output_quantity,
        "difference_kg": (
            input_quantity - output_quantity
        ),
        "source_count": len(edges),
    }


def validate_package_quantity(
    db: Session,
    package_id: int
):
    package = (
        db.query(PackageBatch)
        .filter(PackageBatch.id == package_id)
        .first()
    )

    if not package:
        return {
            "valid": False,
            "reason": "Package batch not found",
        }

    blend = (
        db.query(BlendBatch)
        .filter(
            BlendBatch.id == package.blend_batch_id
        )
        .first()
    )

    if not blend:
        return {
            "valid": False,
            "reason": "Source blend batch not found",
        }

    package_quantity = (
        package.quantity_kg or 0
    )

    blend_quantity = (
        blend.output_quantity_kg or 0
    )

    return {
        "valid": package_quantity <= blend_quantity,
        "package_id": package_id,
        "package_quantity_kg": package_quantity,
        "blend_output_quantity_kg": blend_quantity,
        "remaining_blend_quantity_kg": (
            blend_quantity - package_quantity
        ),
    }


def validate_package_trace(
    db: Session,
    package_id: int
):
    package = (
        db.query(PackageBatch)
        .filter(PackageBatch.id == package_id)
        .first()
    )

    if not package:
        return {
            "valid": False,
            "package_id": package_id,
            "reason": "Package batch not found",
            "checks": []
        }

    checks = []

    calculated_package_quantity = (
        (package.pack_size_kg or 0)
        * (package.number_of_packages or 0)
    )

    package_quantity_valid = (
        abs(
            calculated_package_quantity
            - (package.quantity_kg or 0)
        ) <= 0.001
    )

    checks.append({
        "check": "PACKAGE_QUANTITY",
        "valid": package_quantity_valid,
        "message": (
            "Package quantity matches pack configuration"
            if package_quantity_valid
            else "Package quantity does not match pack configuration"
        )
    })

    blend = (
        db.query(BlendBatch)
        .filter(
            BlendBatch.id == package.blend_batch_id
        )
        .first()
    )

    if not blend:
        checks.append({
            "check": "PACKAGE_BLEND",
            "valid": False,
            "message": "Source blend batch not found"
        })

        return {
            "valid": False,
            "package_id": package_id,
            "checks": checks
        }

    package_vs_blend = (
        package.quantity_kg
        <= blend.output_quantity_kg
    )

    checks.append({
        "check": "PACKAGE_TO_BLEND",
        "valid": package_vs_blend,
        "message": (
            "Package quantity is supported by blend output"
            if package_vs_blend
            else "Package quantity exceeds blend output"
        )
    })

    blend_edges = (
        db.query(BatchEdge)
        .filter(
            BatchEdge.target_type == "BLEND_BATCH",
            BatchEdge.target_id == blend.id,
            BatchEdge.relationship_type == "BLENDED_INTO"
        )
        .all()
    )

    blend_input = sum(
        edge.quantity_kg or 0
        for edge in blend_edges
    )

    blend_quantity_valid = (
        blend_input >= blend.output_quantity_kg
    )

    checks.append({
        "check": "BLEND_INPUT",
        "valid": blend_quantity_valid,
        "message": (
            "Blend output is supported by linked inputs"
            if blend_quantity_valid
            else "Blend output exceeds linked inputs"
        ),
        "input_quantity_kg": blend_input,
        "output_quantity_kg": blend.output_quantity_kg
    })

    for edge in blend_edges:

        auction = (
            db.query(AuctionLot)
            .filter(
                AuctionLot.id == edge.source_id
            )
            .first()
        )

        if not auction:
            checks.append({
                "check": "AUCTION_SOURCE",
                "valid": False,
                "message": (
                    f"Auction lot {edge.source_id} not found"
                )
            })
            continue

        auction_quantity_valid = (
            (edge.quantity_kg or 0)
            <= auction.quantity_kg
        )

        checks.append({
            "check": "AUCTION_ALLOCATION",
            "valid": auction_quantity_valid,
            "auction_lot": auction.auction_lot_code,
            "message": (
                "Blend allocation is within auction quantity"
                if auction_quantity_valid
                else "Blend allocation exceeds auction quantity"
            )
        })

        warehouse_lot = (
            db.query(WarehouseLot)
            .filter(
                WarehouseLot.id ==
                auction.warehouse_lot_id
            )
            .first()
        )

        if not warehouse_lot:
            checks.append({
                "check": "AUCTION_WAREHOUSE",
                "valid": False,
                "message": (
                    f"Warehouse lot for "
                    f"{auction.auction_lot_code} not found"
                )
            })
            continue

        warehouse_edge = (
            db.query(BatchEdge)
            .filter(
                BatchEdge.source_type == "WAREHOUSE_LOT",
                BatchEdge.source_id == warehouse_lot.id,
                BatchEdge.target_type == "AUCTION_LOT",
                BatchEdge.target_id == auction.id,
                BatchEdge.relationship_type == "SOLD_FROM"
            )
            .first()
        )

        warehouse_link_valid = (
            warehouse_edge is not None
            and (
                warehouse_edge.quantity_kg or 0
            ) >= auction.quantity_kg
        )

        checks.append({
            "check": "WAREHOUSE_TO_AUCTION",
            "valid": warehouse_link_valid,
            "auction_lot": auction.auction_lot_code,
            "message": (
                "Warehouse-to-auction allocation is recorded"
                if warehouse_link_valid
                else "Warehouse-to-auction allocation is missing or insufficient"
            )
        })

        factory_batch = (
            db.query(FactoryBatch)
            .filter(
                FactoryBatch.id ==
                warehouse_lot.factory_batch_id
            )
            .first()
        )

        if not factory_batch:
            checks.append({
                "check": "WAREHOUSE_FACTORY",
                "valid": False,
                "message": "Factory batch not found"
            })
            continue

        warehouse_factory_valid = (
            warehouse_lot.quantity_kg
            <= factory_batch.output_quantity_kg
        )

        checks.append({
            "check": "WAREHOUSE_TO_FACTORY",
            "valid": warehouse_factory_valid,
            "message": (
                "Warehouse quantity is supported by factory output"
                if warehouse_factory_valid
                else "Warehouse quantity exceeds factory output"
            )
        })

        green_leaf = (
            db.query(GreenLeafLot)
            .filter(
                GreenLeafLot.id ==
                factory_batch.source_lot_id
            )
            .first()
        )

        if not green_leaf:
            checks.append({
                "check": "FACTORY_SOURCE",
                "valid": False,
                "message": "Green leaf source lot not found"
            })
            continue

        factory_input_valid = (
            factory_batch.input_quantity_kg
            <= green_leaf.quantity_kg
        )

        factory_output_valid = (
            factory_batch.output_quantity_kg
            <= factory_batch.input_quantity_kg
        )

        checks.append({
            "check": "FACTORY_INPUT",
            "valid": factory_input_valid,
            "message": (
                "Factory input is supported by green leaf lot"
                if factory_input_valid
                else "Factory input exceeds green leaf quantity"
            )
        })

        checks.append({
            "check": "FACTORY_OUTPUT",
            "valid": factory_output_valid,
            "message": (
                "Factory output does not exceed factory input"
                if factory_output_valid
                else "Factory output exceeds factory input"
            )
        })

    overall_valid = all(
        check["valid"]
        for check in checks
    )

    return {
        "valid": overall_valid,
        "package_id": package.id,
        "package_code": package.package_code,
        "checks": checks
    }