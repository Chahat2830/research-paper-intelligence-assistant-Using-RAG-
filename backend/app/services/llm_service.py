
"""Groq LLM service for research-paper intelligence tasks."""

import logging
from functools import lru_cache

from groq import APIConnectionError, APIStatusError, Groq, RateLimitError

from app.core.config import settings

logger = logging.getLogger(__name__)


class LLMServiceError(Exception):
    """Raised when an LLM request cannot be completed."""


@lru_cache(maxsize=1)
def get_groq_client() -> Groq:
    """Create and cache the Groq API client."""

    settings.validate_api_configuration()

    return Groq(
        api_key=settings.groq_api_key.strip(),
        timeout=60.0,
        max_retries=2,
    )


def generate_response(
    prompt: str,
    system_prompt: str | None = None,
    temperature: float | None = None,
    max_tokens: int | None = None,
) -> str:
    """Generate a text response using the configured Groq model."""

    if not prompt or not prompt.strip():
        raise ValueError("Prompt cannot be empty.")

    effective_temperature = (
        settings.llm_temperature
        if temperature is None
        else temperature
    )
    effective_max_tokens = (
        settings.llm_max_tokens
        if max_tokens is None
        else max_tokens
    )

    if not 0.0 <= effective_temperature <= 2.0:
        raise ValueError("temperature must be between 0.0 and 2.0.")

    if effective_max_tokens <= 0:
        raise ValueError("max_tokens must be greater than zero.")

    messages = []

    if system_prompt and system_prompt.strip():
        messages.append(
            {
                "role": "system",
                "content": system_prompt.strip(),
            }
        )

    messages.append(
        {
            "role": "user",
            "content": prompt.strip(),
        }
    )

    try:
        response = get_groq_client().chat.completions.create(
            model=settings.llm_model,
            messages=messages,
            temperature=effective_temperature,
            max_tokens=effective_max_tokens,
        )

        if not response.choices:
            logger.error("Groq returned no response choices.")
            raise LLMServiceError(
                "The LLM returned no response choices."
            )

        choice = response.choices[0]
        message = choice.message
        content = message.content

        if not content or not content.strip():
            logger.warning(
                "Groq returned empty text. Model=%s, "
                "finish_reason=%s, reasoning_present=%s, usage=%s",
                settings.llm_model,
                choice.finish_reason,
                bool(getattr(message, "reasoning", None)),
                getattr(response, "usage", None),
            )

            raise LLMServiceError(
                "The LLM returned an empty response. "
                "Check the backend logs for response details."
            )

        return content.strip()

    except LLMServiceError:
        raise

    except RateLimitError as exc:
        logger.warning("Groq API rate limit reached.")
        raise LLMServiceError(
            "The AI service is temporarily rate-limited. "
            "Please try again."
        ) from exc

    except APIConnectionError as exc:
        logger.exception("Could not connect to the Groq API.")
        raise LLMServiceError(
            "Could not connect to the AI service. "
            "Check your internet connection."
        ) from exc

    except APIStatusError as exc:
        logger.error(
            "Groq API returned HTTP status %s: %s",
            exc.status_code,
            str(exc),
        )
        raise LLMServiceError(
            f"The AI service returned HTTP {exc.status_code}. "
            "Check the backend logs for details."
        ) from exc

    except Exception as exc:
        logger.exception("Unexpected error during LLM generation.")
        raise LLMServiceError(
            "An unexpected error occurred while generating "
            "the response."
        ) from exc


def check_llm_connection() -> bool:
    """Check whether the configured Groq model can generate text."""

    response = generate_response(
        prompt="Reply with exactly: OK",
        temperature=0.0,
        max_tokens=50,
    )

    return bool(response.strip())
