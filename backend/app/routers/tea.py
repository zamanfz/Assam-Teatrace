from backend.app.services.quantity_validation import (
    validate_source_allocation,
    validate_blend_quantity,
    validate_package_quantity,
    validate_package_trace,
)
from backend.app.services.audit import create_audit_event
from backend.app.services.lineage import (
    get_factory_batch_lineage
)
from fastapi.responses import Response
from backend.app.services.graph import get_downstream
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.app.models.entities import LabTest
from backend.app.services.compliance import evaluate_lab_test

from backend.app.database.database import get_db

from backend.app.models.entities import (
    Organization,
    User,
    TeaGarden,
    GreenLeafLot,
    FactoryBatch,
    TraceEvent,
    Warehouse,
    WarehouseLot,
    TeaGardenReference,
    AuctionLot,
    BatchEdge,
    BlendBatch,
    PackageBatch,
    QRCodeRecord,
    LabTest
)

from backend.app.schemas.tea import (
    OrganizationCreate,
    OrganizationResponse,
    UserCreate,
    UserResponse,
    GardenCreate,
    GardenResponse,
    GreenLeafLotCreate,
    GreenLeafLotResponse,
    FactoryBatchCreate,
    FactoryBatchResponse,
    TraceEventCreate,
    TraceEventResponse,
    WarehouseCreate,
    WarehouseResponse,
    WarehouseLotCreate,
    WarehouseLotResponse,
    TeaGardenReferenceResponse,
    AuctionLotCreate,
    AuctionLotResponse,
    BatchEdgeCreate,
    BatchEdgeResponse,
    BlendBatchCreate,
    BlendBatchResponse,
    PackageBatchCreate,
    PackageBatchResponse,
    QRCodeCreate,
    QRCodeResponse,
    LabTestCreate,
    LabTestResponse,
)


router = APIRouter(
    prefix="/api",
    tags=["TeaTrace"]
)


@router.post(
    "/organizations",
    response_model=OrganizationResponse
)
def create_organization(
    data: OrganizationCreate,
    db: Session = Depends(get_db)
):
    organization = Organization(
        name=data.name,
        organization_type=data.organization_type
    )

    db.add(organization)
    db.commit()
    db.refresh(organization)

    return organization


@router.get(
    "/organizations",
    response_model=list[OrganizationResponse]
)
def get_organizations(
    db: Session = Depends(get_db)
):
    return db.query(Organization).all()


@router.post(
    "/users",
    response_model=UserResponse
)
def create_user(
    data: UserCreate,
    db: Session = Depends(get_db)
):
    organization = db.get(
        Organization,
        data.organization_id
    )

    if not organization:
        raise HTTPException(
            status_code=404,
            detail="Organization not found"
        )

    user = User(
        name=data.name,
        email=data.email,
        role=data.role,
        organization_id=data.organization_id
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


@router.get(
    "/users",
    response_model=list[UserResponse]
)
def get_users(
    db: Session = Depends(get_db)
):
    return db.query(User).all()


@router.post(
    "/gardens",
    response_model=GardenResponse
)
def create_garden(
    data: GardenCreate,
    db: Session = Depends(get_db)
):
    organization = db.get(
        Organization,
        data.organization_id
    )

    if not organization:
        raise HTTPException(
            status_code=404,
            detail="Organization not found"
        )

    existing = db.query(TeaGarden).filter(
        TeaGarden.garden_code == data.garden_code
    ).first()

    if existing:
        raise HTTPException(
            status_code=400,
            detail="Garden code already exists"
        )

    garden = TeaGarden(
        garden_code=data.garden_code,
        name=data.name,
        district=data.district,
        state=data.state,
        latitude=data.latitude,
        longitude=data.longitude,
        area_hectares=data.area_hectares,
        organization_id=data.organization_id
    )

    db.add(garden)
    db.commit()
    db.refresh(garden)

    return garden


@router.get(
    "/gardens",
    response_model=list[GardenResponse]
)
def get_gardens(
    db: Session = Depends(get_db)
):
    return db.query(TeaGarden).all()


@router.post(
    "/green-leaf-lots",
    response_model=GreenLeafLotResponse
)
def create_green_leaf_lot(
    data: GreenLeafLotCreate,
    db: Session = Depends(get_db)
):
    garden = db.get(
        TeaGarden,
        data.garden_id
    )

    if not garden:
        raise HTTPException(
            status_code=404,
            detail="Tea garden not found"
        )

    existing = db.query(GreenLeafLot).filter(
        GreenLeafLot.lot_code == data.lot_code
    ).first()

    if existing:
        raise HTTPException(
            status_code=400,
            detail="Lot code already exists"
        )

    lot = GreenLeafLot(
        lot_code=data.lot_code,
        garden_id=data.garden_id,
        harvest_date=data.harvest_date,
        quantity_kg=data.quantity_kg,
        quality_grade=data.quality_grade,
        notes=data.notes
    )

    db.add(lot)
    db.commit()
    db.refresh(lot)

    return lot


@router.get(
    "/green-leaf-lots",
    response_model=list[GreenLeafLotResponse]
)
def get_green_leaf_lots(
    db: Session = Depends(get_db)
):
    return db.query(GreenLeafLot).all()

@router.post(
    "/factory-batches",
    response_model=FactoryBatchResponse
)
def create_factory_batch(
    data: FactoryBatchCreate,
    db: Session = Depends(get_db)
):
    source_lot = db.get(
        GreenLeafLot,
        data.source_lot_id
    )

    if not source_lot:
        raise HTTPException(
            status_code=404,
            detail="Green leaf lot not found"
        )

    existing = db.query(FactoryBatch).filter(
        FactoryBatch.batch_code == data.batch_code
    ).first()

    if existing:
        raise HTTPException(
            status_code=400,
            detail="Batch code already exists"
        )

    if data.output_quantity_kg > data.input_quantity_kg:
        raise HTTPException(
            status_code=400,
            detail="Output quantity cannot exceed input quantity"
        )

    batch = FactoryBatch(
        batch_code=data.batch_code,
        source_lot_id=data.source_lot_id,
        factory_name=data.factory_name,
        processing_date=data.processing_date,
        input_quantity_kg=data.input_quantity_kg,
        output_quantity_kg=data.output_quantity_kg,
        tea_type=data.tea_type
    )

    db.add(batch)
    db.commit()
    db.refresh(batch)

    return batch


@router.get(
    "/factory-batches",
    response_model=list[FactoryBatchResponse]
)
def get_factory_batches(
    db: Session = Depends(get_db)
):
    return db.query(FactoryBatch).all()

@router.post(
    "/trace-events",
    response_model=TraceEventResponse
)
def create_trace_event(
    data: TraceEventCreate,
    db: Session = Depends(get_db)
):
    existing = db.query(TraceEvent).filter(
        TraceEvent.event_code == data.event_code
    ).first()

    if existing:
        raise HTTPException(
            status_code=400,
            detail="Event code already exists"
        )

    event = TraceEvent(
        event_code=data.event_code,
        entity_type=data.entity_type,
        entity_id=data.entity_id,
        event_type=data.event_type,
        actor=data.actor,
        location=data.location,
        notes=data.notes
    )

    db.add(event)
    db.commit()
    db.refresh(event)

    return event


@router.get(
    "/trace-events",
    response_model=list[TraceEventResponse]
)
def get_trace_events(
    db: Session = Depends(get_db)
):
    return db.query(
        TraceEvent
    ).order_by(
        TraceEvent.timestamp.asc()
    ).all()

@router.get(
    "/factory-batches/{batch_id}/lineage"
)
def get_batch_lineage(
    batch_id: int,
    db: Session = Depends(get_db)
):
    lineage = get_factory_batch_lineage(
        db,
        batch_id
    )

    if not lineage:
        raise HTTPException(
            status_code=404,
            detail="Factory batch not found"
        )

    return lineage

@router.post(
    "/warehouses",
    response_model=WarehouseResponse
)
def create_warehouse(
    data: WarehouseCreate,
    db: Session = Depends(get_db)
):
    organization = db.get(
        Organization,
        data.organization_id
    )

    if not organization:
        raise HTTPException(
            status_code=404,
            detail="Organization not found"
        )

    existing = db.query(Warehouse).filter(
        Warehouse.warehouse_code == data.warehouse_code
    ).first()

    if existing:
        raise HTTPException(
            status_code=400,
            detail="Warehouse code already exists"
        )

    warehouse = Warehouse(
        warehouse_code=data.warehouse_code,
        name=data.name,
        district=data.district,
        state=data.state,
        capacity_kg=data.capacity_kg,
        organization_id=data.organization_id
    )

    db.add(warehouse)
    db.commit()
    db.refresh(warehouse)

    return warehouse


@router.get(
    "/warehouses",
    response_model=list[WarehouseResponse]
)
def get_warehouses(
    db: Session = Depends(get_db)
):
    return db.query(Warehouse).all()

@router.post(
    "/warehouse-lots",
    response_model=WarehouseLotResponse
)
def create_warehouse_lot(
    data: WarehouseLotCreate,
    db: Session = Depends(get_db)
):
    batch = db.get(
        FactoryBatch,
        data.factory_batch_id
    )

    if not batch:
        raise HTTPException(
            status_code=404,
            detail="Factory batch not found"
        )

    warehouse = db.get(
        Warehouse,
        data.warehouse_id
    )

    if not warehouse:
        raise HTTPException(
            status_code=404,
            detail="Warehouse not found"
        )

    if data.quantity_kg > batch.output_quantity_kg:
        raise HTTPException(
            status_code=400,
            detail="Warehouse quantity exceeds factory batch output"
        )

    existing = db.query(WarehouseLot).filter(
        WarehouseLot.warehouse_lot_code ==
        data.warehouse_lot_code
    ).first()

    if existing:
        raise HTTPException(
            status_code=400,
            detail="Warehouse lot code already exists"
        )

    warehouse_lot = WarehouseLot(
        warehouse_lot_code=data.warehouse_lot_code,
        factory_batch_id=data.factory_batch_id,
        warehouse_id=data.warehouse_id,
        quantity_kg=data.quantity_kg,
        received_at=data.received_at
    )

    db.add(warehouse_lot)
    db.commit()
    db.refresh(warehouse_lot)

    return warehouse_lot


@router.get(
    "/warehouse-lots",
    response_model=list[WarehouseLotResponse]
)
def get_warehouse_lots(
    db: Session = Depends(get_db)
):
    return db.query(WarehouseLot).all()

@router.get(
    "/tea-garden-references",
    response_model=list[TeaGardenReferenceResponse]
)
def get_tea_garden_references(
    db: Session = Depends(get_db)
):
    return db.query(TeaGardenReference).all()
@router.post(
    "/auction-lots",
    response_model=AuctionLotResponse,
    status_code=201
)
def create_auction_lot(
    payload: AuctionLotCreate,
    db: Session = Depends(get_db)
):
    warehouse_lot = db.query(WarehouseLot).filter(
        WarehouseLot.id == payload.warehouse_lot_id
    ).first()

    if not warehouse_lot:
        raise HTTPException(
            status_code=404,
            detail="Warehouse lot not found"
        )

    if payload.quantity_kg <= 0:
        raise HTTPException(
            status_code=400,
            detail="Auction quantity must be greater than zero"
        )

    if payload.quantity_kg > warehouse_lot.quantity_kg:
        raise HTTPException(
            status_code=400,
            detail="Auction quantity cannot exceed warehouse lot quantity"
        )

    existing = db.query(AuctionLot).filter(
        AuctionLot.auction_lot_code == payload.auction_lot_code
    ).first()

    if existing:
        raise HTTPException(
            status_code=400,
            detail="Auction lot code already exists"
        )

    auction_lot = AuctionLot(
        auction_lot_code=payload.auction_lot_code,
        warehouse_lot_id=payload.warehouse_lot_id,
        auction_center=payload.auction_center,
        auction_date=payload.auction_date,
        quantity_kg=payload.quantity_kg,
        grade=payload.grade,
        buyer_name=payload.buyer_name,
        sale_price_per_kg=payload.sale_price_per_kg,
        status=payload.status
    )

    db.add(auction_lot)
    db.commit()
    db.refresh(auction_lot)

    return auction_lot


@router.get(
    "/auction-lots",
    response_model=list[AuctionLotResponse]
)
def get_auction_lots(
    db: Session = Depends(get_db)
):
    return db.query(AuctionLot).all()

@router.post(
    "/lineage/edges",
    response_model=BatchEdgeResponse,
    status_code=201
)
def create_batch_edge(
    payload: BatchEdgeCreate,
    db: Session = Depends(get_db)
):
    source_type = payload.source_type.upper()
    target_type = payload.target_type.upper()

    if payload.quantity_kg is not None and payload.quantity_kg <= 0:
        raise HTTPException(
            status_code=400,
            detail="Quantity must be greater than zero"
        )

    if payload.quantity_kg is not None:

        validation = validate_source_allocation(
            db=db,
            entity_type=source_type,
            entity_id=payload.source_id
        )

        if validation["source_quantity_kg"] is None:
            raise HTTPException(
                status_code=404,
                detail="Source entity or quantity not found"
            )

        available_quantity = (
            validation["source_quantity_kg"]
            - validation["allocated_quantity_kg"]
        )

        if payload.quantity_kg > available_quantity:
            raise HTTPException(
                status_code=400,
                detail=(
                    "Quantity allocation exceeds available "
                    f"source quantity. Available: "
                    f"{available_quantity:.3f} kg"
                )
            )

    if (
        source_type == "AUCTION_LOT"
        and target_type == "BLEND_BATCH"
    ):
        source = db.query(AuctionLot).filter(
            AuctionLot.id == payload.source_id
        ).first()

        target = db.query(BlendBatch).filter(
            BlendBatch.id == payload.target_id
        ).first()

        if not source:
            raise HTTPException(
                status_code=404,
                detail="Source auction lot not found"
            )

        if not target:
            raise HTTPException(
                status_code=404,
                detail="Target blend batch not found"
            )

    edge = BatchEdge(
        source_type=source_type,
        source_id=payload.source_id,
        target_type=target_type,
        target_id=payload.target_id,
        relationship_type=payload.relationship_type,
        quantity_kg=payload.quantity_kg
    )

    db.add(edge)
    db.commit()
    db.refresh(edge)

    return edge


@router.get(
    "/lineage/edges",
    response_model=list[BatchEdgeResponse]
)
def get_batch_edges(
    db: Session = Depends(get_db)
):
    return db.query(BatchEdge).all()

@router.get("/lineage/{entity_type}/{entity_id}")
def get_lineage(
    entity_type: str,
    entity_id: int,
    db: Session = Depends(get_db)
):
    return {
        "entity_type": entity_type,
        "entity_id": entity_id,
        "edges": get_downstream(
            db,
            entity_type,
            entity_id
        )
    }

@router.post(
    "/blend-batches",
    response_model=BlendBatchResponse,
    status_code=201
)
def create_blend_batch(
    payload: BlendBatchCreate,
    db: Session = Depends(get_db)
):
    if payload.output_quantity_kg <= 0:
        raise HTTPException(
            status_code=400,
            detail="Blend output quantity must be greater than zero"
        )

    existing = db.query(BlendBatch).filter(
        BlendBatch.blend_code == payload.blend_code
    ).first()

    if existing:
        raise HTTPException(
            status_code=400,
            detail="Blend code already exists"
        )

    blend = BlendBatch(
        blend_code=payload.blend_code,
        blend_date=payload.blend_date,
        output_quantity_kg=payload.output_quantity_kg,
        tea_type=payload.tea_type,
        status=payload.status,
        notes=payload.notes
    )

    db.add(blend)
    db.commit()
    db.refresh(blend)

    return blend


@router.get(
    "/blend-batches",
    response_model=list[BlendBatchResponse]
)
def get_blend_batches(
    db: Session = Depends(get_db)
):
    return db.query(BlendBatch).all()

@router.get("/blend-batches/{blend_id}/validate")
def validate_blend_batch(
    blend_id: int,
    db: Session = Depends(get_db)
):
    blend = db.query(BlendBatch).filter(
        BlendBatch.id == blend_id
    ).first()

    if not blend:
        raise HTTPException(
            status_code=404,
            detail="Blend batch not found"
        )

    edges = db.query(BatchEdge).filter(
        BatchEdge.target_type == "BLEND_BATCH",
        BatchEdge.target_id == blend_id,
        BatchEdge.relationship_type == "BLENDED_INTO"
    ).all()

    total_input = sum(
        edge.quantity_kg or 0
        for edge in edges
    )

    output = blend.output_quantity_kg

    if total_input < output:
        return {
            "blend_id": blend.id,
            "blend_code": blend.blend_code,
            "input_quantity_kg": total_input,
            "output_quantity_kg": output,
            "status": "INVALID",
            "message": "Blend output exceeds linked input quantity."
        }

    return {
        "blend_id": blend.id,
        "blend_code": blend.blend_code,
        "input_quantity_kg": total_input,
        "output_quantity_kg": output,
        "status": "VALID",
        "message": "Blend quantity is supported by linked source material."
    }

@router.post(
    "/package-batches",
    response_model=PackageBatchResponse,
    status_code=201
)
def create_package_batch(
    payload: PackageBatchCreate,
    db: Session = Depends(get_db)
):
    if payload.quantity_kg <= 0:
        raise HTTPException(
            status_code=400,
            detail="Package quantity must be greater than zero"
        )

    if payload.pack_size_kg <= 0:
        raise HTTPException(
            status_code=400,
            detail="Pack size must be greater than zero"
        )

    if payload.number_of_packages <= 0:
        raise HTTPException(
            status_code=400,
            detail="Number of packages must be greater than zero"
        )

    calculated_quantity = (
        payload.pack_size_kg * payload.number_of_packages
    )

    if abs(calculated_quantity - payload.quantity_kg) > 0.001:
        raise HTTPException(
            status_code=400,
            detail="Quantity does not match pack size multiplied by number of packages"
        )

    blend = db.query(BlendBatch).filter(
        BlendBatch.id == payload.blend_batch_id
    ).first()

    if not blend:
        raise HTTPException(
            status_code=404,
            detail="Blend batch not found"
        )

    if payload.quantity_kg > blend.output_quantity_kg:
        raise HTTPException(
            status_code=400,
            detail="Package quantity cannot exceed blend output quantity"
        )

    existing = db.query(PackageBatch).filter(
        PackageBatch.package_code == payload.package_code
    ).first()

    if existing:
        raise HTTPException(
            status_code=400,
            detail="Package code already exists"
        )

    package = PackageBatch(
        package_code=payload.package_code,
        blend_batch_id=payload.blend_batch_id,
        packaging_date=payload.packaging_date,
        quantity_kg=payload.quantity_kg,
        pack_size_kg=payload.pack_size_kg,
        number_of_packages=payload.number_of_packages,
        brand_name=payload.brand_name,
        status=payload.status
    )

    db.add(package)
    db.commit()
    db.refresh(package)

    return package


@router.get(
    "/package-batches",
    response_model=list[PackageBatchResponse]
)
def get_package_batches(
    db: Session = Depends(get_db)
):
    return db.query(PackageBatch).all()

@router.post(
    "/qr-codes",
    response_model=QRCodeResponse,
    status_code=201
)
def create_qr_code(
    payload: QRCodeCreate,
    db: Session = Depends(get_db)
):
    package = db.query(PackageBatch).filter(
        PackageBatch.id == payload.package_batch_id
    ).first()

    if not package:
        raise HTTPException(
            status_code=404,
            detail="Package batch not found"
        )

    existing = db.query(QRCodeRecord).filter(
        QRCodeRecord.qr_code == payload.qr_code
    ).first()

    if existing:
        raise HTTPException(
            status_code=400,
            detail="QR code already exists"
        )

    public_url = (
        f"http://127.0.0.1:8000/public/trace/"
        f"{payload.qr_code}"
    )

    qr_record = QRCodeRecord(
        qr_code=payload.qr_code,
        package_batch_id=payload.package_batch_id,
        public_url=public_url,
        status="ACTIVE"
    )

    db.add(qr_record)
    db.commit()
    db.refresh(qr_record)

    return qr_record

@router.get("/qr-codes/{qr_code}/image")
def get_qr_image(
    qr_code: str,
    db: Session = Depends(get_db)
):
    qr_record = db.query(QRCodeRecord).filter(
        QRCodeRecord.qr_code == qr_code
    ).first()

    if not qr_record:
        raise HTTPException(
            status_code=404,
            detail="QR code not found"
        )

    from backend.app.services.qr import generate_qr_png

    image = generate_qr_png(qr_record.public_url)

    return Response(
        content=image,
        media_type="image/png"
    )

@router.get("/public/trace/{qr_code}")
def public_trace(
    qr_code: str,
    db: Session = Depends(get_db)
):
    qr_record = db.query(QRCodeRecord).filter(
        QRCodeRecord.qr_code == qr_code,
        QRCodeRecord.status == "ACTIVE"
    ).first()

    if not qr_record:
        raise HTTPException(
            status_code=404,
            detail="QR code not found or inactive"
        )

    package = db.query(PackageBatch).filter(
        PackageBatch.id == qr_record.package_batch_id
    ).first()

    if not package:
        raise HTTPException(
            status_code=404,
            detail="Package batch not found"
        )

    blend = db.query(BlendBatch).filter(
        BlendBatch.id == package.blend_batch_id
    ).first()

    if not blend:
        raise HTTPException(
            status_code=404,
            detail="Blend batch not found"
        )

    edges = db.query(BatchEdge).filter(
        BatchEdge.target_type == "BLEND_BATCH",
        BatchEdge.target_id == blend.id,
        BatchEdge.relationship_type == "BLENDED_INTO"
    ).all()

    auction_lots = []

    for edge in edges:
        auction = db.query(AuctionLot).filter(
            AuctionLot.id == edge.source_id
        ).first()

        if not auction:
            continue

        warehouse_lot = db.query(WarehouseLot).filter(
            WarehouseLot.id == auction.warehouse_lot_id
        ).first()

        warehouse = None

        if warehouse_lot:
            warehouse = db.query(Warehouse).filter(
                Warehouse.id == warehouse_lot.warehouse_id
            ).first()

        factory_batch = None
        green_leaf = None
        garden = None

        if warehouse_lot:
            factory_batch = db.query(FactoryBatch).filter(
                FactoryBatch.id == warehouse_lot.factory_batch_id
            ).first()

        if factory_batch:
            green_leaf = db.query(GreenLeafLot).filter(
                GreenLeafLot.id == factory_batch.source_lot_id
            ).first()

        if green_leaf:
            garden = db.query(TeaGarden).filter(
                TeaGarden.id == green_leaf.garden_id
            ).first()

        auction_lots.append({
            "auction_lot": {
                "code": auction.auction_lot_code,
                "auction_center": auction.auction_center,
                "auction_date": auction.auction_date,
                "grade": auction.grade,
                "quantity_kg": edge.quantity_kg
            },
            "warehouse": {
                "name": warehouse.name if warehouse else None,
                "district": warehouse.district if warehouse else None
            },
            "factory": {
                "batch_code": factory_batch.batch_code
                if factory_batch else None,
                "factory_name": factory_batch.factory_name
                if factory_batch else None,
                "processing_date": factory_batch.processing_date
                if factory_batch else None
            },
            "green_leaf": {
                "lot_code": green_leaf.lot_code
                if green_leaf else None,
                "harvest_date": green_leaf.harvest_date
                if green_leaf else None
            },
            "garden": {
                "garden_code": garden.garden_code
                if garden else None,
                "name": garden.name
                if garden else None,
                "district": garden.district
                if garden else None,
                "state": garden.state
                if garden else None,
                "latitude": garden.latitude
                if garden else None,
                "longitude": garden.longitude
                if garden else None
            }
        })
    lab_tests = db.query(LabTest).filter(
        LabTest.package_batch_id == package.id
    ).all()

    compliance_results = []

    for lab_test in lab_tests:
        evaluation = evaluate_lab_test(db, lab_test.id)

        if evaluation:
            compliance_results.append({
    "parameter_name": evaluation.get("parameter_name"),
    "result_status": evaluation.get("result_status"),
    "maximum_allowed": evaluation.get("maximum_allowed"),
    "unit": evaluation.get("unit"),
    "rule_source": (
        evaluation.get("rule", {}).get("source_name")
        if evaluation.get("rule")
        else None
    ),
    "rule_code": (
        evaluation.get("rule", {}).get("rule_code")
        if evaluation.get("rule")
        else None
    )
})

    if not compliance_results:
        overall_compliance = "NOT_EVALUATED"
    elif any(
        result["result_status"] == "FAIL"
        for result in compliance_results
    ):
        overall_compliance = "FAIL"
    elif any(
        result["result_status"] == "INCONCLUSIVE"
        for result in compliance_results
    ):
        overall_compliance = "INCONCLUSIVE"
    elif any(
        result["result_status"] == "UNKNOWN"
        for result in compliance_results
    ):
        overall_compliance = "UNKNOWN"
    elif all(
        result["result_status"] == "PASS"
        for result in compliance_results
    ):
        overall_compliance = "PASS"
    else:
        overall_compliance = "NOT_EVALUATED"

    return {
        "trace_status": "TRACEABLE",

        "package": {
            "package_code": package.package_code,
            "brand_name": package.brand_name,
            "quantity_kg": package.quantity_kg,
            "pack_size_kg": package.pack_size_kg,
            "number_of_packages": package.number_of_packages,
            "packaging_date": package.packaging_date
        },

        "blend": {
            "blend_code": blend.blend_code,
            "tea_type": blend.tea_type,
            "output_quantity_kg": blend.output_quantity_kg,
            "blend_date": blend.blend_date
        },

        "sources": auction_lots,

        "compliance": {
            "overall_status": overall_compliance,
            "tests": compliance_results
        }
    }

@router.post(
    "/lab-tests",
    response_model=LabTestResponse,
    status_code=201
)
def create_lab_test(
    payload: LabTestCreate,
    db: Session = Depends(get_db)
):
    package = db.query(PackageBatch).filter(
        PackageBatch.id == payload.package_batch_id
    ).first()

    if not package:
        raise HTTPException(
            status_code=404,
            detail="Package batch not found"
        )

    existing = db.query(LabTest).filter(
        LabTest.test_code == payload.test_code
    ).first()

    if existing:
        raise HTTPException(
            status_code=400,
            detail="Test code already exists"
        )

    allowed_statuses = {
        "PASS",
        "FAIL",
        "UNKNOWN",
        "INCONCLUSIVE",
        "NOT_EVALUATED"
    }

    if payload.result_status not in allowed_statuses:
        raise HTTPException(
            status_code=400,
            detail="Invalid result status"
        )

    test = LabTest(
        test_code=payload.test_code,
        package_batch_id=payload.package_batch_id,
        test_type=payload.test_type,
        parameter_name=payload.parameter_name,
        measured_value=payload.measured_value,
        unit=payload.unit,
        result_status=payload.result_status,
        laboratory_name=payload.laboratory_name,
        test_date=payload.test_date,
        report_reference=payload.report_reference,
        notes=payload.notes
    )

    db.add(test)
    db.commit()
    db.refresh(test)

    create_audit_event(
    db=db,
    event_type="LAB_TEST_CREATED",
    entity_type="LAB_TEST",
    entity_id=test.id,
    actor=payload.laboratory_name,
    event_data={
        "test_code": test.test_code,
        "package_batch_id": test.package_batch_id,
        "test_type": test.test_type,
        "parameter_name": test.parameter_name,
        "result_status": test.result_status,
        "test_date": test.test_date
    }
)

    return test


@router.get(
    "/lab-tests",
    response_model=list[LabTestResponse]
)
def get_lab_tests(
    db: Session = Depends(get_db)
):
    return db.query(LabTest).all()

@router.get("/lineage/validate/{entity_type}/{entity_id}")
def validate_lineage_quantity(
    entity_type: str,
    entity_id: int,
    db: Session = Depends(get_db)
):
    entity_type = entity_type.upper()

    if entity_type == "BLEND_BATCH":
        return validate_blend_quantity(
            db=db,
            blend_id=entity_id
        )

    if entity_type == "PACKAGE_BATCH":
        return validate_package_quantity(
            db=db,
            package_id=entity_id
        )

    return validate_source_allocation(
        db=db,
        entity_type=entity_type,
        entity_id=entity_id
    )

@router.get("/lineage/validate/package/{package_id}")
def validate_package_trace_endpoint(
    package_id: int,
    db: Session = Depends(get_db)
):
    result = validate_package_trace(
        db=db,
        package_id=package_id
    )
    return result