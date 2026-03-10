"""
Vapi / Retell middleware for General Intellect.

Usage:
    from generalintelect import GIClient
    from generalintelect.vapi import with_memory

    gi = GIClient(url=os.getenv("GI_URL"), agent_id="support-bot")

    @with_memory(gi)
    def handle_webhook(payload: dict) -> dict:
        context = payload["_gi_context"]  # injected automatically
        response = llm.complete(system_prompt + context + user_message)
        return {"response": response}
"""

from .client import AsyncGIClient, GIClient


def with_memory(gi: GIClient):
    """Decorator for synchronous Vapi/Retell webhook handlers."""

    def decorator(handler):
        def wrapper(payload: dict, **kwargs):
            call_id = _extract_call_id(payload)
            message = _extract_message(payload)

            context = ""
            if message:
                try:
                    context = gi.recall(query=message, namespace=call_id)
                except Exception:
                    pass

            payload["_gi_context"] = context
            result = handler(payload, **kwargs)

            if message:
                try:
                    gi.remember(content=message, namespace=call_id)
                except Exception:
                    pass

            return result

        return wrapper

    return decorator


def async_with_memory(gi: AsyncGIClient):
    """Decorator for async Vapi/Retell webhook handlers."""

    def decorator(handler):
        async def wrapper(payload: dict, **kwargs):
            call_id = _extract_call_id(payload)
            message = _extract_message(payload)

            context = ""
            if message:
                try:
                    context = await gi.recall(query=message, namespace=call_id)
                except Exception:
                    pass

            payload["_gi_context"] = context
            result = await handler(payload, **kwargs)

            if message:
                try:
                    await gi.remember(content=message, namespace=call_id)
                except Exception:
                    pass

            return result

        return wrapper

    return decorator


def _extract_call_id(payload: dict) -> str:
    # Vapi
    call_id = payload.get("call", {}).get("id")
    if call_id:
        return call_id
    # Retell
    call_id = payload.get("call_id")
    if call_id:
        return call_id
    return "default"


def _extract_message(payload: dict) -> str:
    # Vapi: full transcript
    transcript = payload.get("transcript")
    if transcript:
        return transcript
    # Vapi: single message
    message = payload.get("message", {}).get("content")
    if message:
        return message
    # Retell
    return payload.get("transcript", "")
