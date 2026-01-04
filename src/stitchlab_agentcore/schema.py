from pydantic import BaseModel
from typing import Optional, Any
import uuid
from .utils import denormalize_email


class AgentInvocationAttachment(BaseModel):
    type: str
    value: str

    def read_attachment(self) -> str:
        return self.value


class AgentInvocationPayload(BaseModel):
    actor_id: str
    session_id: str
    trace_id: str
    message: str
    attachments: Optional[list[dict[str, Any]]] = None

    @classmethod
    def from_input_dict(cls, input_data: dict):
        """
        Create an AgentInvocationPayload instance from an input dict, such as payload['input'].
        """
        return cls(
            actor_id=input_data.get('actor_id'),
            session_id=input_data.get('session_id'),
            trace_id=str(uuid.uuid4()),
            message=input_data.get('message'),
            attachments=input_data.get('attachments', None)
        )

    @property
    def invocation_state(self) -> dict:
        if self.attachments:
            return {
                'attachments' : self.attachments
            }
        return {}

    @property
    def denormalized_actor_id(self) -> str:
        try:
            return denormalize_email(self.actor_id)
        except Exception as e:
            return self.actor_id