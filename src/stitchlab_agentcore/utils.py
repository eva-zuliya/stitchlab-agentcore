import base64


def normalize_email(email: str) -> str:
    return base64.urlsafe_b64encode(email.encode("utf-8")).decode("ascii").rstrip("=")


def denormalize_email(value: str) -> str:
    padding = "=" * (-len(value) % 4)
    return base64.urlsafe_b64decode((value + padding).encode("ascii")).decode("utf-8")