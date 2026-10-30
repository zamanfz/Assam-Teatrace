from datetime import datetime

from sqlalchemy import (
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text
)

from sqlalchemy.orm import relationship

from backend.app.database.database import Base


class Organization(Base):
    __tablename__ = "organizations"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String(200), nullable=False)
    organization_type = Column(String(50), nullable=False)

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    users = relationship(
        "User",
        back_populates="organization"
    )

    gardens = relationship(
        "TeaGarden",
        back_populates="organization"
    )


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String(150), nullable=False)
    email = Column(String(200), unique=True, nullable=False)
    role = Column(String(50), nullable=False)

    organization_id = Column(
        Integer,
        ForeignKey("organizations.id"),
        nullable=False
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    organization = relationship(
        "Organization",
        back_populates="users"
    )


class TeaGarden(Base):
    __tablename__ = "tea_gardens"

    id = Column(Integer, primary_key=True, index=True)

    garden_code = Column(
        String(50),
        unique=True,
        nullable=False
    )

    name = Column(String(200), nullable=False)

    district = Column(String(100), nullable=False)

    state = Column(
        String(100),
        default="Assam",
        nullable=False
    )

    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)

    area_hectares = Column(Float, nullable=True)

    organization_id = Column(
        Integer,
        ForeignKey("organizations.id"),
        nullable=False
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    organization = relationship(
        "Organization",
        back_populates="gardens"
    )

    green_leaf_lots = relationship(
        "GreenLeafLot",
        back_populates="garden"
    )


class GreenLeafLot(Base):
    __tablename__ = "green_leaf_lots"

    id = Column(Integer, primary_key=True, index=True)

    lot_code = Column(
        String(50),
        unique=True,
        nullable=False
    )

    garden_id = Column(
        Integer,
        ForeignKey("tea_gardens.id"),
        nullable=False
    )

    harvest_date = Column(
        DateTime,
        nullable=False
    )

    quantity_kg = Column(
        Float,
        nullable=False
    )

    quality_grade = Column(
        String(50),
        nullable=True
    )

    status = Column(
        String(50),
        default="HARVESTED",
        nullable=False
    )

    notes = Column(
        Text,
        nullable=True
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    garden = relationship(
        "TeaGarden",
        back_populates="green_leaf_lots"
    )

    factory_batches = relationship(
    "FactoryBatch",
    back_populates="source_lot"
    )

class FactoryBatch(Base):
    __tablename__ = "factory_batches"

    id = Column(Integer, primary_key=True, index=True)

    batch_code = Column(
        String(50),
        unique=True,
        nullable=False
    )

    source_lot_id = Column(
        Integer,
        ForeignKey("green_leaf_lots.id"),
        nullable=False
    )

    factory_name = Column(
        String(200),
        nullable=False
    )

    processing_date = Column(
        DateTime,
        nullable=False
    )

    input_quantity_kg = Column(
        Float,
        nullable=False
    )

    output_quantity_kg = Column(
        Float,
        nullable=False
    )

    tea_type = Column(
        String(100),
        nullable=True
    )

    status = Column(
        String(50),
        default="PROCESSED",
        nullable=False
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    source_lot = relationship(
        "GreenLeafLot",
        back_populates="factory_batches"
    )


class TraceEvent(Base):
    __tablename__ = "trace_events"

    id = Column(Integer, primary_key=True, index=True)

    event_code = Column(
        String(50),
        unique=True,
        nullable=False
    )

    entity_type = Column(
        String(50),
        nullable=False
    )

    entity_id = Column(
        Integer,
        nullable=False
    )

    event_type = Column(
        String(100),
        nullable=False
    )

    actor = Column(
        String(150),
        nullable=False
    )

    location = Column(
        String(200),
        nullable=True
    )

    notes = Column(
        Text,
        nullable=True
    )

    timestamp = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )


class Warehouse(Base):
    __tablename__ = "warehouses"

    id = Column(Integer, primary_key=True, index=True)

    warehouse_code = Column(
        String(50),
        unique=True,
        nullable=False
    )

    name = Column(
        String(200),
        nullable=False
    )

    district = Column(
        String(100),
        nullable=False
    )

    state = Column(
        String(100),
        default="Assam",
        nullable=False
    )

    capacity_kg = Column(
        Float,
        nullable=True
    )

    organization_id = Column(
        Integer,
        ForeignKey("organizations.id"),
        nullable=False
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    organization = relationship(
        "Organization"
    )

    warehouse_lots = relationship(
        "WarehouseLot",
        back_populates="warehouse"
    )


class WarehouseLot(Base):
    __tablename__ = "warehouse_lots"

    id = Column(Integer, primary_key=True, index=True)

    warehouse_lot_code = Column(
        String(50),
        unique=True,
        nullable=False
    )

    factory_batch_id = Column(
        Integer,
        ForeignKey("factory_batches.id"),
        nullable=False
    )

    warehouse_id = Column(
        Integer,
        ForeignKey("warehouses.id"),
        nullable=False
    )

    quantity_kg = Column(
        Float,
        nullable=False
    )

    received_at = Column(
        DateTime,
        nullable=False
    )

    status = Column(
        String(50),
        default="STORED",
        nullable=False
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    factory_batch = relationship(
        "FactoryBatch"
    )

    warehouse = relationship(
        "Warehouse",
        back_populates="warehouse_lots"
    )

class TeaGardenReference(Base):
    __tablename__ = "tea_garden_references"

    id = Column(Integer, primary_key=True, index=True)
    garden_name = Column(String, nullable=False)
    district = Column(String, nullable=False)
    year = Column(Integer, nullable=False)

    geographical_area_hectares = Column(Float, nullable=True)
    plantation_area_hectares = Column(Float, nullable=True)

    own_green_leaf_kg = Column(Float, nullable=True)
    purchased_green_leaf_kg = Column(Float, nullable=True)

    manufactured_black_tea_kg = Column(Float, nullable=True)
    manufactured_green_tea_kg = Column(Float, nullable=True)
    manufactured_orthodox_tea_kg = Column(Float, nullable=True)

    source_name = Column(String, nullable=False)
    source_reference = Column(String, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

class AuctionLot(Base):
    __tablename__ = "auction_lots"

    id = Column(Integer, primary_key=True, index=True)
    auction_lot_code = Column(String, unique=True, nullable=False, index=True)

    warehouse_lot_id = Column(
        Integer,
        ForeignKey("warehouse_lots.id"),
        nullable=False
    )

    auction_center = Column(String, nullable=False)
    auction_date = Column(DateTime, nullable=False)

    quantity_kg = Column(Float, nullable=False)
    grade = Column(String, nullable=True)

    buyer_name = Column(String, nullable=True)
    sale_price_per_kg = Column(Float, nullable=True)

    status = Column(String, default="SOLD")

    created_at = Column(DateTime, default=datetime.utcnow)

    warehouse_lot = relationship("WarehouseLot")

class BatchEdge(Base):
    __tablename__ = "batch_edges"

    id = Column(Integer, primary_key=True, index=True)

    source_type = Column(String, nullable=False)
    source_id = Column(Integer, nullable=False)

    target_type = Column(String, nullable=False)
    target_id = Column(Integer, nullable=False)

    relationship_type = Column(String, nullable=False)

    quantity_kg = Column(Float, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

class BlendBatch(Base):
    __tablename__ = "blend_batches"

    id = Column(Integer, primary_key=True, index=True)

    blend_code = Column(
        String,
        unique=True,
        nullable=False,
        index=True
    )

    blend_date = Column(DateTime, nullable=False)

    output_quantity_kg = Column(
        Float,
        nullable=False
    )

    tea_type = Column(
        String,
        nullable=False
    )

    status = Column(
        String,
        default="CREATED"
    )

    notes = Column(
        String,
        nullable=True
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

class PackageBatch(Base):
    __tablename__ = "package_batches"

    id = Column(Integer, primary_key=True, index=True)

    package_code = Column(
        String,
        unique=True,
        nullable=False,
        index=True
    )

    blend_batch_id = Column(
        Integer,
        ForeignKey("blend_batches.id"),
        nullable=False
    )

    packaging_date = Column(
        DateTime,
        nullable=False
    )

    quantity_kg = Column(
        Float,
        nullable=False
    )

    pack_size_kg = Column(
        Float,
        nullable=False
    )

    number_of_packages = Column(
        Integer,
        nullable=False
    )

    brand_name = Column(
        String,
        nullable=False
    )

    status = Column(
        String,
        default="PACKAGED"
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    blend_batch = relationship("BlendBatch")

class QRCodeRecord(Base):
    __tablename__ = "qr_codes"

    id = Column(Integer, primary_key=True, index=True)

    qr_code = Column(
        String,
        unique=True,
        nullable=False,
        index=True
    )

    package_batch_id = Column(
        Integer,
        ForeignKey("package_batches.id"),
        nullable=False
    )

    public_url = Column(
        String,
        nullable=False
    )

    status = Column(
        String,
        default="ACTIVE"
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    package_batch = relationship("PackageBatch")

class LabTest(Base):
    __tablename__ = "lab_tests"

    id = Column(Integer, primary_key=True, index=True)

    test_code = Column(
        String,
        unique=True,
        nullable=False,
        index=True
    )

    package_batch_id = Column(
        Integer,
        ForeignKey("package_batches.id"),
        nullable=False
    )

    test_type = Column(
        String,
        nullable=False
    )

    parameter_name = Column(
        String,
        nullable=False
    )

    measured_value = Column(
        Float,
        nullable=True
    )

    unit = Column(
        String,
        nullable=False
    )

    result_status = Column(
        String,
        default="UNKNOWN"
    )

    laboratory_name = Column(
        String,
        nullable=True
    )

    test_date = Column(
        DateTime,
        nullable=False
    )

    report_reference = Column(
        String,
        nullable=True
    )

    notes = Column(
        String,
        nullable=True
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    package_batch = relationship("PackageBatch")

class ComplianceRule(Base):
    __tablename__ = "compliance_rules"

    id = Column(Integer, primary_key=True, index=True)

    rule_code = Column(
        String,
        unique=True,
        nullable=False,
        index=True
    )

    parameter_name = Column(
        String,
        nullable=False
    )

    product_type = Column(
        String,
        nullable=False
    )

    jurisdiction = Column(
        String,
        nullable=False
    )

    maximum_value = Column(
        Float,
        nullable=False
    )

    unit = Column(
        String,
        nullable=False
    )

    source_name = Column(
        String,
        nullable=False
    )

    source_reference = Column(
        String,
        nullable=True
    )

    effective_date = Column(
        DateTime,
        nullable=True
    )

    status = Column(
        String,
        default="ACTIVE"
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

class AuditEvent(Base):
    __tablename__ = "audit_events"

    id = Column(Integer, primary_key=True, index=True)
    event_type = Column(String, nullable=False)
    entity_type = Column(String, nullable=False)
    entity_id = Column(Integer, nullable=False)
    actor = Column(String, nullable=True)
    event_data = Column(String, nullable=False)
    previous_hash = Column(String, nullable=True)
    event_hash = Column(String, nullable=False, unique=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)