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
    agent_name: str
    actor_id: str
    actor_attributes: Optional[dict[str, Any]] = None
    session_id: str
    trace_id: str
    message: str
    is_streaming_response: bool = True
    attachments: Optional[list[dict[str, Any]]] = None

    @classmethod
    def from_input_dict(cls, input_data: dict):
        """
        Create an AgentInvocationPayload instance from an input dict, such as payload['input'].
        """
        return cls(
            agent_name=input_data.get('agent_name', '__DEFAULT__'),
            actor_id=input_data.get('actor_id'),
            actor_attributes=input_data.get('actor_attributes', None),
            session_id=input_data.get('session_id'),
            trace_id=str(uuid.uuid4()),
            message=input_data.get('message'),
            is_streaming_response=input_data.get('is_streaming_response', True),
            attachments=input_data.get('attachments', None)
        )

    @property
    def invocation_state(self) -> dict:
        state = {}
        if self.attachments:
            state['attachments'] = self.attachments
        
        if self.actor_attributes:
            state['actor_attributes'] = self.actor_attributes

        return state

    @property
    def denormalized_actor_id(self) -> str:
        try:
            return denormalize_email(self.actor_id)
        except Exception as e:
            return self.actor_id