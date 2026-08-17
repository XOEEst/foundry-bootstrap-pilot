from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

PROTOCOL_NAME = "responses"
PROTOCOL_VERSION = "2.0.0"
DEFAULT_MODEL = "gpt-5.4-mini"
MODEL_ENVIRONMENT_VARIABLE = "AZURE_AI_MODEL_DEPLOYMENT_NAME"
AGENT_ID = "policy-ready-unbound"
ROLE_SUMMARY = "A ready-unbound policy helper fixture with no existing Foundry binding metadata."


@dataclass(frozen=True)
class ResponseEnvelope:
    agent_id: str
    output_text: str
    model: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": f"{self.agent_id}-local-response",
            "object": "response",
            "protocol": {"name": PROTOCOL_NAME, "version": PROTOCOL_VERSION},
            "model": self.model,
            "output": [
                {
                    "type": "message",
                    "role": "assistant",
                    "content": [{"type": "output_text", "text": self.output_text}],
                }
            ],
            "output_text": self.output_text,
        }


@dataclass
class LocalPilotResponsesHost:
    agent_id: str
    role_summary: str
    default_reply: str
    model: str = DEFAULT_MODEL

    def start(self) -> dict[str, str]:
        return {
            "agent_id": self.agent_id,
            "runtime": "python",
            "protocol_name": PROTOCOL_NAME,
            "protocol_version": PROTOCOL_VERSION,
            "model": self.model,
        }

    def create_response(self, *, input_text: str) -> ResponseEnvelope:
        clean_input = " ".join(str(input_text).split()) or "Hello"
        return ResponseEnvelope(
            agent_id=self.agent_id,
            output_text=f"{self.default_reply} Request: {clean_input}",
            model=self.model,
        )


def _extract_input(payload: dict[str, Any] | None) -> str:
    if not payload:
        return "Hello"
    raw_input = payload.get("input", "")
    if isinstance(raw_input, str):
        return raw_input
    if isinstance(raw_input, list):
        parts: list[str] = []
        for item in raw_input:
            if isinstance(item, str):
                parts.append(item)
                continue
            if not isinstance(item, dict):
                continue
            contents = item.get("content", [])
            if isinstance(contents, list):
                for content in contents:
                    if isinstance(content, str):
                        parts.append(content)
                    elif isinstance(content, dict):
                        text = content.get("text") or content.get("input_text")
                        if isinstance(text, str):
                            parts.append(text)
        joined = " ".join(part for part in parts if part)
        return joined or "Hello"
    return "Hello"


def build_local_app() -> LocalPilotResponsesHost:
    return LocalPilotResponsesHost(
        agent_id=AGENT_ID,
        role_summary=ROLE_SUMMARY,
        default_reply="Policy helper fixture ready.",
    )


def invoke(payload: dict[str, Any] | None = None) -> dict[str, Any]:
    response = build_local_app().create_response(input_text=_extract_input(payload))
    return response.to_dict()


def main() -> int:
    print(json.dumps(invoke({"input": "pilot smoke test"}), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
