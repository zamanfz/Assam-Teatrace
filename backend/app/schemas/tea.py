from datetime import datetime

from pydantic import BaseModel, Field


class OrganizationCreate(BaseModel):
    name: str
    organization_type: str


class OrganizationResponse(BaseModel):
    id: int
    name: str
    organization_type: str

    class Config:
        from_attributes = True


class UserCreate(BaseModel):
    name: str
    email: str
    role: str
    organization_id: int


class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    role: str
    organization_id: int

    class Config:
        from_attributes = True


class GardenCreate(BaseModel):
    garden_code: str
    name: str
    district: str
    state: str = "Assam"
    latitude: float | None = None
    longitude: float | None = None
    area_hectares: float | None = None
    organization_id: int


class GardenResponse(BaseModel):
    id: int
    garden_code: str
    name: str
    district: str
    state: str
    latitude: float | None
    longitude: float | None
    area_hectares: float | None
    organization_id: int

    class Config:
        from_attributes = True


class GreenLeafLotCreate(BaseModel):
    lot_code: str
    garden_id: int
    harvest_date: datetime
    quantity_kg: float = Field(gt=0)
    quality_grade: str | None = None
    notes: str | None = None


class GreenLeafLotResponse(BaseModel):
    id: int
    lot_code: str
    garden_id: int
    harvest_date: datetime
    quantity_kg: float
    quality_grade: str | None
    status: str
    notes: str | None

    class Config:
        from_attributes = True

class FactoryBatchCreate(BaseModel):
    batch_code: str
    source_lot_id: int
    factory_name: str
    processing_date: datetime
    input_quantity_kg: float = Field(gt=0)
    output_quantity_kg: float = Field(gt=0)
    tea_type: str | None = None


class FactoryBatchResponse(BaseModel):
    id: int
    batch_code: str
    source_lot_id: int
    factory_name: str
    processing_date: datetime
    input_quantity_kg: float
    output_quantity_kg: float
    tea_type: str | None
    status: str

    class Config:
        from_attributes = True


class TraceEventCreate(BaseModel):
    event_code: str
    entity_type: str
    entity_id: int
    event_type: str
    actor: str
    location: str | None = None
    notes: str | None = None


class TraceEventResponse(BaseModel):
    id: int
    event_code: str
    entity_type: str
    entity_id: int
    event_type: str
    actor: str
    location: str | None
    notes: str | None
    timestamp: datetime

    class Config:
        from_attributes = True

class WarehouseCreate(BaseModel):
    warehouse_code: str
    name: str
    district: str
    state: str = "Assam"
    capacity_kg: float | None = None
    organization_id: int


class WarehouseResponse(BaseModel):
    id: int
    warehouse_code: str
    name: str
    district: str
    state: str
    capacity_kg: float | None
    organization_id: int

    class Config:
        from_attributes = True


class WarehouseLotCreate(BaseModel):
    warehouse_lot_code: str
    factory_batch_id: int
    warehouse_id: int
    quantity_kg: float = Field(gt=0)
    received_at: datetime


class WarehouseLotResponse(BaseModel):
    id: int
    warehouse_lot_code: str
    factory_batch_id: int
    warehouse_id: int
    quantity_kg: float
    received_at: datetime
    status: str

    class Config:
        from_attributes = True

class TeaGardenReferenceResponse(BaseModel):
    id: int
    garden_name: str
    district: str
    year: int
    geographical_area_hectares: float | None
    plantation_area_hectares: float | None
    own_green_leaf_kg: float | None
    purchased_green_leaf_kg: float | None
    manufactured_black_tea_kg: float | None
    manufactured_green_tea_kg: float | None
    manufactured_orthodox_tea_kg: float | None
    source_name: str
    source_reference: str | None

    class Config:
        from_attributes = True

class AuctionLotCreate(BaseModel):
    auction_lot_code: str
    warehouse_lot_id: int
    auction_center: str
    auction_date: datetime
    quantity_kg: float
    grade: str | None = None
    buyer_name: str | None = None
    sale_price_per_kg: float | None = None
    status: str = "SOLD"


class AuctionLotResponse(AuctionLotCreate):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class BatchEdgeCreate(BaseModel):
    source_type: str
    source_id: int
    target_type: str
    target_id: int
    relationship_type: str
    quantity_kg: float | None = None


class BatchEdgeResponse(BatchEdgeCreate):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class BlendBatchCreate(BaseModel):
    blend_code: str
    blend_date: datetime
    output_quantity_kg: float
    tea_type: str
    status: str = "CREATED"
    notes: str | None = None


class BlendBatchResponse(BlendBatchCreate):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class PackageBatchCreate(BaseModel):
    package_code: str
    blend_batch_id: int
    packaging_date: datetime
    quantity_kg: float
    pack_size_kg: float
    number_of_packages: int
    brand_name: str
    status: str = "PACKAGED"


class PackageBatchResponse(PackageBatchCreate):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class QRCodeCreate(BaseModel):
    qr_code: str
    package_batch_id: int


class QRCodeResponse(QRCodeCreate):
    id: int
    public_url: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True

class LabTestCreate(BaseModel):
    test_code: str
    package_batch_id: int
    test_type: str
    parameter_name: str
    measured_value: float | None = None
    unit: str
    result_status: str = "UNKNOWN"
    laboratory_name: str | None = None
    test_date: datetime
    report_reference: str | None = None
    notes: str | None = None


class LabTestResponse(LabTestCreate):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
class ComplianceRuleCreate(BaseModel):
    rule_code: str
    parameter_name: str
    product_type: str
    jurisdiction: str
    maximum_value: float
    unit: str
    source_name: str
    source_reference: str | None = None
    effective_date: datetime | None = None
    status: str = "ACTIVE"


class ComplianceRuleResponse(ComplianceRuleCreate):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True