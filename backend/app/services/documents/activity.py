import json
from app.models.models import DocumentActivity


def record_activity(db, document, actor_id, event_type, summary, details=None, ip_address=None):
    activity = DocumentActivity(
        document_id=document.id,
        organization_id=document.organization_id,
        actor_id=actor_id,
        event_type=event_type,
        summary=summary[:500],
        details_json=json.dumps(details or {}, ensure_ascii=False, default=str),
        ip_address=ip_address,
    )
    db.add(activity)
    db.flush()
    return activity
