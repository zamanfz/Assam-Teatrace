from sqlalchemy.orm import Session

from backend.app.models.entities import (
    FactoryBatch,
    GreenLeafLot,
    TeaGarden
)


def get_factory_batch_lineage(
    db: Session,
    batch_id: int
):
    batch = db.get(FactoryBatch, batch_id)

    if not batch:
        return None

    lot = db.get(
        GreenLeafLot,
        batch.source_lot_id
    )

    garden = None

    if lot:
        garden = db.get(
            TeaGarden,
            lot.garden_id
        )

    return {
        "factory_batch": {
            "id": batch.id,
            "batch_code": batch.batch_code,
            "factory_name": batch.factory_name,
            "processing_date": batch.processing_date,
            "input_quantity_kg": batch.input_quantity_kg,
            "output_quantity_kg": batch.output_quantity_kg,
            "tea_type": batch.tea_type,
            "status": batch.status
        },
        "source_green_leaf_lot": {
            "id": lot.id,
            "lot_code": lot.lot_code,
            "harvest_date": lot.harvest_date,
            "quantity_kg": lot.quantity_kg,
            "quality_grade": lot.quality_grade,
            "status": lot.status
        } if lot else None,
        "source_garden": {
            "id": garden.id,
            "garden_code": garden.garden_code,
            "name": garden.name,
            "district": garden.district,
            "state": garden.state,
            "latitude": garden.latitude,
            "longitude": garden.longitude,
            "area_hectares": garden.area_hectares
        } if garden else None
    }