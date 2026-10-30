import csv
from pathlib import Path

from sqlalchemy.orm import Session

from backend.app.models.entities import TeaGardenReference


def import_tea_garden_reference(
    db: Session,
    csv_path: str
):
    path = Path(csv_path)

    if not path.exists():
        raise FileNotFoundError(f"CSV file not found: {csv_path}")

    imported = 0

    with path.open("r", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for row in reader:
            record = TeaGardenReference(
                garden_name=row["garden_name"],
                district=row["district"],
                year=int(row["year"]),
                geographical_area_hectares=float(
                    row["geographical_area_hectares"]
                ),
                plantation_area_hectares=float(
                    row["plantation_area_hectares"]
                ),
                own_green_leaf_kg=float(
                    row["own_green_leaf_kg"]
                ),
                purchased_green_leaf_kg=float(
                    row["purchased_green_leaf_kg"]
                ),
                manufactured_black_tea_kg=float(
                    row["manufactured_black_tea_kg"]
                ),
                manufactured_green_tea_kg=float(
                    row["manufactured_green_tea_kg"]
                ),
                manufactured_orthodox_tea_kg=float(
                    row["manufactured_orthodox_tea_kg"]
                ),
                source_name=row["source_name"],
                source_reference=row["source_reference"],
            )

            db.add(record)
            imported += 1

    db.commit()

    return imported