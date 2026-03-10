from fastapi import HTTPException


def validate_identity(agent_id: str, namespace: str) -> None:
    """Validate that agent_id and namespace are present and well-formed.

    This is the extension point for multi-tenant ACL — add token verification,
    org-level namespace restrictions, or per-agent allowlists here in v2.
    """
    if not agent_id or not agent_id.strip():
        raise HTTPException(status_code=400, detail="agent_id is required")
    if not namespace or not namespace.strip():
        raise HTTPException(status_code=400, detail="namespace is required")
