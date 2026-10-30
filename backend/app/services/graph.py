from sqlalchemy.orm import Session

from backend.app.models.entities import BatchEdge


def get_downstream(
    db: Session,
    entity_type: str,
    entity_id: int
):
    visited = set()
    results = []

    def traverse(current_type, current_id):
        key = (current_type, current_id)

        if key in visited:
            return

        visited.add(key)

        edges = (
            db.query(BatchEdge)
            .filter(
                BatchEdge.source_type == current_type,
                BatchEdge.source_id == current_id
            )
            .all()
        )

        for edge in edges:
            results.append({
                "source_type": edge.source_type,
                "source_id": edge.source_id,
                "target_type": edge.target_type,
                "target_id": edge.target_id,
                "relationship_type": edge.relationship_type,
                "quantity_kg": edge.quantity_kg
            })

            traverse(
                edge.target_type,
                edge.target_id
            )

    traverse(entity_type, entity_id)

    return results