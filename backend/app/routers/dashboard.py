from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.database.database import get_db
from backend.app.models.entities import (
    TeaGarden,
    FactoryBatch,
    BlendBatch,
    PackageBatch,
    LabTest
)
from backend.app.services.audit import verify_audit_chain
from backend.app.services.compliance import evaluate_lab_test

router = APIRouter(
    prefix="/api/dashboard",
    tags=["Dashboard"]
)


@router.get("/summary")
def dashboard_summary(
    db: Session = Depends(get_db)
):
    lab_tests = db.query(LabTest).all()

    compliance = {
        "total": len(lab_tests),
        "pass": 0,
        "fail": 0,
        "unknown": 0,
        "inconclusive": 0,
        "not_evaluated": 0
    }

    for test in lab_tests:
        evaluation = evaluate_lab_test(db, test.id)

        if not evaluation:
            continue

        status = evaluation.get("result_status")

        if status == "PASS":
            compliance["pass"] += 1
        elif status == "FAIL":
            compliance["fail"] += 1
        elif status == "UNKNOWN":
            compliance["unknown"] += 1
        elif status == "INCONCLUSIVE":
            compliance["inconclusive"] += 1
        elif status == "NOT_EVALUATED":
            compliance["not_evaluated"] += 1

    audit_result = verify_audit_chain(db)

    return {
        "counts": {
            "gardens": db.query(TeaGarden).count(),
            "factory_batches": db.query(FactoryBatch).count(),
            "blend_batches": db.query(BlendBatch).count(),
            "packages": db.query(PackageBatch).count()
        },
        "compliance": compliance,
        "audit": audit_result,
        "system": {
            "traceability": "ACTIVE",
            "compliance_engine": "ACTIVE",
            "qr_verification": "ACTIVE"
        }
    }