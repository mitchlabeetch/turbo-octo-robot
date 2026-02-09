from typing import Any, Dict


def parse_gmail_webhook(payload: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "provider": "gmail",
        "subject": payload.get("subject"),
        "body": payload.get("body"),
        "contact_email": payload.get("from"),
        "metadata_json": payload.get("raw")
    }


def parse_microsoft_webhook(payload: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "provider": "microsoft",
        "subject": payload.get("subject"),
        "body": payload.get("body"),
        "contact_email": payload.get("from"),
        "metadata_json": payload.get("raw")
    }
