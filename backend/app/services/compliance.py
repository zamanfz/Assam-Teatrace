from sqlalchemy.orm import Session

from backend.app.models.entities import LabTest, ComplianceRule


def evaluate_lab_test(db: Session, test_id: int):
    lab_test = db.query(LabTest).filter(
        LabTest.id == test_id
    ).first()

    if not lab_test:
        return None

    rule = db.query(ComplianceRule).filter(
        ComplianceRule.parameter_name == lab_test.parameter_name,
        ComplianceRule.product_type == "TEA",
        ComplianceRule.jurisdiction == "INDIA",
        ComplianceRule.status == "ACTIVE",
        ComplianceRule.effective_date <= lab_test.test_date
    ).order_by(
        ComplianceRule.effective_date.desc()
    ).first()

    if not rule:
        return {
            "test_code": lab_test.test_code,
            "parameter_name": lab_test.parameter_name,
            "measured_value": lab_test.measured_value,
            "unit": lab_test.unit,
            "result_status": "NOT_EVALUATED",
            "reason": "No applicable active compliance rule found",
            "rule": None
        }

    if lab_test.measured_value is None:
        return {
            "test_code": lab_test.test_code,
            "parameter_name": lab_test.parameter_name,
            "measured_value": None,
            "unit": lab_test.unit,
            "result_status": "UNKNOWN",
            "reason": "Measured value is missing",
            "rule": {
                "rule_code": rule.rule_code,
                "maximum_value": rule.maximum_value,
                "unit": rule.unit,
                "source_name": rule.source_name,
                "source_reference": rule.source_reference
            }
        }

    if lab_test.unit != rule.unit:
        return {
            "test_code": lab_test.test_code,
            "parameter_name": lab_test.parameter_name,
            "measured_value": lab_test.measured_value,
            "unit": lab_test.unit,
            "result_status": "INCONCLUSIVE",
            "reason": "Laboratory unit does not match compliance rule unit",
            "rule": {
                "rule_code": rule.rule_code,
                "maximum_value": rule.maximum_value,
                "unit": rule.unit,
                "source_name": rule.source_name,
                "source_reference": rule.source_reference
            }
        }

    if lab_test.measured_value <= rule.maximum_value:
        result = "PASS"
    else:
        result = "FAIL"

    return {
        "test_code": lab_test.test_code,
        "parameter_name": lab_test.parameter_name,
        "measured_value": lab_test.measured_value,
        "unit": lab_test.unit,
        "result_status": result,
        "maximum_allowed": rule.maximum_value,
        "reason": (
            "Measured value is within the applicable compliance limit"
            if result == "PASS"
            else "Measured value exceeds the applicable compliance limit"
        ),
        "rule": {
            "rule_code": rule.rule_code,
            "maximum_value": rule.maximum_value,
            "unit": rule.unit,
            "source_name": rule.source_name,
            "source_reference": rule.source_reference,
            "effective_date": rule.effective_date
        }
    }