from typing import Any, Awaitable, Callable, Dict, List, Optional

from pydantic import Field

from guardrails_api_client import CallInputs as ICallInputs
from guardrails.classes.history.inputs import Inputs
from guardrails.classes.generic.arbitrary_model import ArbitraryModel


class CallInputs(Inputs, ICallInputs, ArbitraryModel):
    llm_api: Optional[Callable[[Any], Awaitable[Any]]] = Field(
        description="The LLM function provided by the user"
        "during Guard.__call__ or Guard.parse.",
        default=None,
    )
    prompt: Optional[str] = Field(
        description="The prompt string as provided by the user.", default=None
    )
    instructions: Optional[str] = Field(
        description="The instructions string as provided by the user.", default=None
    )
    args: List[Any] = Field(
        description="Additional arguments for the LLM as provided by the user.",
        default_factory=list,
    )
    kwargs: Dict[str, Any] = Field(
        description="Additional keyword-arguments for the LLM as provided by the user.",
        default_factory=dict,
    )

    def to_interface(self) -> ICallInputs:
        inputs = super().to_interface().to_dict() or {}
        inputs["args"] = self.args
        # TODO: Better way to prevent creds from being logged,
        #   if they're passed in as kwargs to the LLM
        redacted_kwargs = {}
        for k, v in self.kwargs.items():
            if "key" in k.lower() or "token" in k.lower():
                redaction_length = len(v) - 4
                redacted_kwargs[k] = f"{"*"*redaction_length}{v[-4:]}"
            else:
                redacted_kwargs[k] = v
        inputs["kwargs"] = redacted_kwargs
        return ICallInputs(**inputs)

    def to_dict(self) -> Dict[str, Any]:
        return self.to_interface().to_dict()

    @classmethod
    def from_interface(cls, i_call_inputs: ICallInputs) -> "CallInputs":
        inputs = i_call_inputs.to_dict()
        return cls(**inputs)

    @classmethod
    def from_dict(cls, obj: Dict[str, Any]):
        i_call_inputs = ICallInputs.from_dict(obj) or ICallInputs()

        return cls.from_interface(i_call_inputs)
