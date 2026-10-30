from datetime import datetime

from backend.app.models.entities import TeaGarden, GreenLeafLot, BatchEdge, Organization
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.app.database.database import Base
from backend.app.models import entities  # Register all ORM models
from backend.app.services.quantity_validation import (
    validate_source_allocation,
    validate_blend_quantity,
    validate_package_quantity,
    validate_package_trace,
)


@pytest.fixture
def db():
    """Create an isolated in-memory database for each test."""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    TestingSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
    )

    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()

    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


def test_missing_source_returns_invalid(db):
    result = validate_source_allocation(
        db, "GREEN_LEAF_LOT", 999999
    )

    assert result["valid"] is False
    assert "reason" in result


def test_missing_blend_returns_invalid(db):
    result = validate_blend_quantity(db, 999999)

    assert result["valid"] is False
    assert result["reason"] == "Blend batch not found"


def test_missing_package_returns_invalid(db):
    result = validate_package_quantity(db, 999999)

    assert result["valid"] is False
    assert result["reason"] == "Package batch not found"


def test_missing_package_trace_returns_invalid(db):
    result = validate_package_trace(db, 999999)

    assert result["valid"] is False
    assert result["checks"] == []
    assert result["reason"] == "Package batch not found"

def test_missing_source_returns_invalid(db):
    result = validate_source_allocation(db, "GREEN_LEAF_LOT", 999999)
    assert result["valid"] is False
    assert "reason" in result

def test_source_allocation_exceeding_available_quantity_is_invalid(db):
    organization = Organization(
        name="Test Organization",
        organization_type="TEA_GARDEN",
    )
    db.add(organization)
    db.flush()

    garden = TeaGarden(
        garden_code="TEST-GARDEN-001",
        name="Test Tea Garden",
        district="Dibrugarh",
        state="Assam",
        organization_id=organization.id,
    )
    db.add(garden)
    db.flush()

    lot = GreenLeafLot(
        lot_code="TEST-GL-001",
        garden_id=garden.id,
        harvest_date=datetime(2026, 10, 30),
        quantity_kg=100.0,
        status="HARVESTED",
    )
    db.add(lot)
    db.flush()

    db.add(
        BatchEdge(
            source_type="GREEN_LEAF_LOT",
            source_id=lot.id,
            target_type="FACTORY_BATCH",
            target_id=1,
            relationship_type="PROCESSED_INTO",
            quantity_kg=120.0,
        )
    )
    db.commit()

    result = validate_source_allocation(db, "GREEN_LEAF_LOT", lot.id)

    assert result["valid"] is False
    assert result["source_quantity_kg"] == 100.0
    assert result["allocated_quantity_kg"] == 120.0