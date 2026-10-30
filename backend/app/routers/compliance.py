from backend.app.services.audit import create_audit_event, verify_audit_chain
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.services.compliance import evaluate_lab_test
from backend.app.database.database import get_db
from backend.app.models.entities import ComplianceRule
from backend.app.schemas.compliance import (
    ComplianceRuleCreate,
    ComplianceRuleResponse
)

router = APIRouter(
    prefix="/api/compliance-rules",
    tags=["Compliance Rules"]
)


@router.post("/", response_model=ComplianceRuleResponse)
def create_compliance_rule(
    rule: ComplianceRuleCreate,
    db: Session = Depends(get_db)
):
    existing = db.query(ComplianceRule).filter(
        ComplianceRule.rule_code == rule.rule_code
    ).first()

    if existing:
        raise HTTPException(
            status_code=400,
            detail="Rule code already exists"
        )

    db_rule = ComplianceRule(**rule.model_dump())

    db.add(db_rule)
    db.commit()
    db.refresh(db_rule)

    return db_rule


@router.get("/", response_model=list[ComplianceRuleResponse])
def get_compliance_rules(
    db: Session = Depends(get_db)
):
    return db.query(ComplianceRule).all()

@router.get("/evaluate/{test_id}")
def evaluate_test(
    test_id: int,
    db: Session = Depends(get_db)
):
    result = evaluate_lab_test(db, test_id)

    if result is None:
        raise HTTPException(
            status_code=404,
            detail="Lab test not found"
        )

    return result

@router.post("/audit/test")
def create_test_audit_event(
    db: Session = Depends(get_db)
):
    event = create_audit_event(
        db=db,
        event_type="TEST_EVENT",
        entity_type="PACKAGE_BATCH",
        entity_id=1,
        actor="system",
        event_data={
            "message": "TeaTrace audit chain test",
            "package_code": "PKG-0001"
        }
    )

    return {
        "id": event.id,
        "event_hash": event.event_hash,
        "previous_hash": event.previous_hash
    }


@router.get("/audit/verify")
def verify_audit(
    db: Session = Depends(get_db)
):
    return verify_audit_chain(db)