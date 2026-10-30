from backend.app.database.database import SessionLocal
from backend.app.services.import_reference import import_tea_garden_reference


CSV_PATH = "data/tea_garden_reference.csv"


def main():
    db = SessionLocal()

    try:
        count = import_tea_garden_reference(db, CSV_PATH)
        print(f"Successfully imported {count} tea garden reference records.")
    except Exception as e:
        db.rollback()
        print(f"Import failed: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    main()