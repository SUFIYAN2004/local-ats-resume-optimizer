import os
os.environ["CREWAI_TRACING_ENABLED"] = "false"
os.environ["OTEL_SDK_DISABLED"] = "true"

from crewai import LLM


def get_llm():
    return LLM(
        model="openai/qwen-coder",
        base_url="http://localhost:8000/v1",
        api_key="fake-key",
    )