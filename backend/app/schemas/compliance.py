
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class ComplianceRuleCreate(BaseModel):
    rule_code: str
    parameter_name: str
    product_type: str = "TEA"
    jurisdiction: str = "INDIA"
    maximum_value: float
    unit: str
    source_name: str
    source_reference: Optional[str] = None
    effective_date: Optional[datetime] = None
    status: str = "ACTIVE"


class ComplianceRuleResponse(ComplianceRuleCreate):
    id: int
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class LabTestCreate(BaseModel):
    test_code: str
    package_batch_id: int
    test_type: str
    parameter_name: str
    measured_value: Optional[float] = None
    unit: str
    result_status: str = "UNKNOWN"
    laboratory_name: Optional[str] = None
    test_date: datetime
    report_reference: Optional[str] = None
    notes: Optional[str] = None


class LabTestResponse(LabTestCreate):
    id: int
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
