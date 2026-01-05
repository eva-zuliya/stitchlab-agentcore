import base64

def normalize_email(email: str) -> str:
    return base64.urlsafe_b64encode(email.encode("utf-8")).decode("ascii").rstrip("=")


def denormalize_email(value: str) -> str:
    padding = "=" * (-len(value) % 4)
    return base64.urlsafe_b64decode((value + padding).encode("ascii")).decode("utf-8")


def get_langfuse_prompt(prompt_name: str, variables: dict = None) -> str:
    from .config import GlobalConfig
    cfg = GlobalConfig.get()

    if cfg is None:
        raise TypeError("GlobalConfig is abstract")
    
    if cfg.langfuse is None:
        raise TypeError("GlobalConfig Langfuse is not initialized")

    try:
        prompt = cfg.langfuse.get_prompt(
            name=prompt_name
        )

        if variables is None:
            return prompt.compile()

        return prompt.compile(**variables)

    except Exception as e:
        raise RuntimeError(f"Failed to fetch or compile prompt '{prompt_name}': {e}")