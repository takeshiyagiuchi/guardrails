# WE EXPLICITLY DO NOT WANT TO MOCK LITELLM FOR THE TESTS BELOW.
# THEY ENSURE THAT WE HAVE A STANDARD WAY TO COMMUNICATE WITH THE LIBRARY
#   OVER TIME.


import importlib
import os

import pytest

import guardrails as gd

from typing import List
from pydantic import BaseModel


@pytest.mark.skipif(
    not importlib.util.find_spec("litellm"),
    reason="`litellm` is not installed",
)
@pytest.mark.skipif(
    os.environ.get("OPENAI_API_KEY") in [None, "mocked"],
    reason="openai api key not set",
)
def test_litellm_tools():
    class Fruit(BaseModel):
        name: str
        color: str
        description: str

    class Fruits(BaseModel):
        list: List[Fruit]

    guard = gd.Guard.from_pydantic(Fruits)
    res = guard(
        model="gpt-4o",
        msg_history=[
            {"role": "user", "content": "Name 10 unique fruits, lowercase only"}
        ],
        tools=guard.add_json_function_calling_tool([]),
        tool_choice="required",
    )
    assert res.validated_output


@pytest.mark.skipif(
    not importlib.util.find_spec("litellm"),
    reason="`litellm` is not installed",
)
@pytest.mark.skipif(
    os.environ.get("OPENAI_API_KEY") in [None, "mocked"],
    reason="openai api key not set",
)
def test_litellm_openai():
    from litellm import litellm

    guard = gd.Guard()
    res = guard(
        llm_api=litellm.completion,
        model="gpt-3.5-turbo",
        msg_history=[
            {"role": "user", "content": "Name 10 unique fruits, lowercase only"}
        ],
    )
    assert res.validated_output
    res = guard(
        llm_api=litellm.completion,
        model="gpt-3.5-turbo",
        prompt="Name 10 unique fruits, lowercase only, one per line, no numbers",
    )
    assert res.validated_output


@pytest.mark.skipif(
    not importlib.util.find_spec("litellm"),
    reason="`litellm` is not installed",
)
@pytest.mark.skipif(
    os.environ.get("OPENAI_API_KEY") in [None, "mocked"],
    reason="openai api key not set",
)
def test_litellm_openai_streaming():
    from litellm import litellm

    guard = gd.Guard()
    res = guard(
        llm_api=litellm.completion,
        model="gpt-3.5-turbo",
        prompt="Name 10 unique fruits, lowercase only, one per line, no numbers",
        stream=True,
    )

    for chunk in res:
        assert chunk.validated_output


@pytest.mark.skipif(
    not importlib.util.find_spec("litellm"),
    reason="`litellm` is not installed",
)
@pytest.mark.skipif(
    os.environ.get("OPENAI_API_KEY") in [None, "mocked"],
    reason="openai api key not set",
)
def test_litellm_openai_async():
    import asyncio

    from litellm import litellm

    # from litellm import acompletion
    guard = gd.Guard()
    ares = guard(
        llm_api=litellm.acompletion,
        model="gpt-3.5-turbo",
        prompt="Name 10 unique fruits, lowercase only, one per line, no numbers",
    )

    res = asyncio.run(ares)
    assert res.validated_output
    assert res.validated_output == res.raw_llm_output
    assert len(res.validated_output.split("\n")) == 10


@pytest.mark.skipif(
    os.environ.get("OPENAI_API_KEY") in [None, "mocked"],
    reason="openai api key not set",
)
def test_litellm_openai_async_messages():
    import asyncio

    # from litellm import acompletion
    guard = gd.Guard()
    ares = guard(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "user",
                "content": "Name 10 unique fruits, "
                "lowercase only, one per line, no numbers",
            }
        ],
    )

    res = asyncio.run(ares)
    assert res.validated_output
    assert res.validated_output == res.raw_llm_output
    assert len(res.validated_output.split("\n")) == 10
