import os

from dataclasses import dataclass
from typing import Any

from dotenv import load_dotenv

from groq import (
    Groq,
    APIConnectionError,
    APIStatusError,
)

from src.errors import ProviderInfrastructureError


load_dotenv()


@dataclass
class LLMResult:
    message: Any

    input_tokens: int
    output_tokens: int

    @property
    def total_tokens(self) -> int:
        return (
            self.input_tokens
            + self.output_tokens
        )


class LLMClient:
    def __init__(
        self,
        model: str = "openai/gpt-oss-120b",
    ):
        api_key = os.getenv(
            "GROQ_API_KEY"
        )

        if not api_key:
            raise ValueError(
                "GROQ_API_KEY not found in .env"
            )

        self.client = Groq(
            api_key=api_key,

            # Groq already retries transient failures.
            # Explicit here so project behaviour is clear.
            max_retries=2,

            timeout=60.0,
        )

        self.model = model

    def generate(
        self,
        messages: list,
        tools: list | None = None,
    ) -> LLMResult:

        kwargs = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.2,
            "max_completion_tokens": 4000,
        }

        if tools is not None:
            kwargs["tools"] = tools
            kwargs["tool_choice"] = "auto"

        try:

            response = (
                self.client
                .chat
                .completions
                .create(**kwargs)
            )

        # -------------------------------------------------
        # Network / timeout / connectivity failure
        # -------------------------------------------------

        except APIConnectionError as error:

            raise ProviderInfrastructureError(
                message=(
                    "Groq API connection failed after retries: "
                    f"{error}"
                ),
                provider="groq",
                failure_type="connection_error",
                status_code=None,
            ) from error

        # -------------------------------------------------
        # HTTP response from Groq
        # -------------------------------------------------

        except APIStatusError as error:

            status_code = (
                error.status_code
            )

            # These are transient/provider-side conditions,
            # not failures caused by repository reasoning.
            if (
                status_code in {
                    408,    # request timeout
                    409,    # conflict; retried by Groq SDK
                    429,    # rate limit
                }
                or status_code >= 500
            ):

                if status_code == 429:
                    failure_type = (
                        "rate_limit"
                    )

                elif status_code >= 500:
                    failure_type = (
                        "provider_server_error"
                    )

                else:
                    failure_type = (
                        "provider_transient_error"
                    )

                raise ProviderInfrastructureError(
                    message=(
                        "Groq API infrastructure failure "
                        f"(HTTP {status_code}): {error}"
                    ),
                    provider="groq",
                    failure_type=failure_type,
                    status_code=status_code,
                ) from error

            # 400/401/403/404/422 etc. should NOT
            # automatically be called infrastructure failures.
            raise

        usage = getattr(
            response,
            "usage",
            None,
        )

        input_tokens = 0
        output_tokens = 0

        if usage is not None:

            input_tokens = (
                getattr(
                    usage,
                    "prompt_tokens",
                    0,
                )
                or 0
            )

            output_tokens = (
                getattr(
                    usage,
                    "completion_tokens",
                    0,
                )
                or 0
            )

        return LLMResult(
            message=(
                response
                .choices[0]
                .message
            ),
            input_tokens=input_tokens,
            output_tokens=output_tokens,
        )