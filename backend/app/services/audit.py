import hashlib
import json

from sqlalchemy.orm import Session

from backend.app.models.entities import AuditEvent


def calculate_event_hash(
    event_type: str,
    entity_type: str,
    entity_id: int,
    actor: str | None,
    event_data: dict,
    previous_hash: str | None
) -> str:

    payload = {
        "event_type": event_type,
        "entity_type": entity_type,
        "entity_id": entity_id,
        "actor": actor,
        "event_data": event_data,
        "previous_hash": previous_hash
    }

    serialized = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        default=str
    )

    return hashlib.sha256(
        serialized.encode("utf-8")
    ).hexdigest()


def create_audit_event(
    db: Session,
    event_type: str,
    entity_type: str,
    entity_id: int,
    event_data: dict,
    actor: str | None = None
):

    last_event = db.query(AuditEvent).order_by(
        AuditEvent.id.desc()
    ).first()

    previous_hash = (
        last_event.event_hash
        if last_event
        else None
    )

    event_hash = calculate_event_hash(
        event_type=event_type,
        entity_type=entity_type,
        entity_id=entity_id,
        actor=actor,
        event_data=event_data,
        previous_hash=previous_hash
    )

    audit_event = AuditEvent(
        event_type=event_type,
        entity_type=entity_type,
        entity_id=entity_id,
        actor=actor,
        event_data=json.dumps(
            event_data,
            sort_keys=True,
            default=str
        ),
        previous_hash=previous_hash,
        event_hash=event_hash
    )

    db.add(audit_event)
    db.commit()
    db.refresh(audit_event)

    return audit_event


def verify_audit_chain(db: Session):

    events = db.query(AuditEvent).order_by(
        AuditEvent.id.asc()
    ).all()

    previous_hash = None

    for event in events:

        if event.previous_hash != previous_hash:
            return {
                "valid": False,
                "broken_at_event": event.id,
                "reason": "Previous hash does not match"
            }

        event_data = json.loads(event.event_data)

        expected_hash = calculate_event_hash(
            event_type=event.event_type,
            entity_type=event.entity_type,
            entity_id=event.entity_id,
            actor=event.actor,
            event_data=event_data,
            previous_hash=event.previous_hash
        )

        if event.event_hash != expected_hash:
            return {
                "valid": False,
                "broken_at_event": event.id,
                "reason": "Event hash does not match event contents"
            }

        previous_hash = event.event_hash

    return {
        "valid": True,
        "events_checked": len(events)
    }