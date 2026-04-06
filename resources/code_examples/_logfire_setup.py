"""Shared Logfire setup for code examples.

Configures Logfire + OpenAI instrumentation if LOGFIRE_TOKEN is set in `.env`.
Import this module and wrap each example entrypoint with `run_example(...)`
to emit query-friendly spans for each example execution.
"""

from __future__ import annotations

import logging
import os
import sys
from contextlib import contextmanager
from contextlib import nullcontext
from typing import Awaitable
from typing import TypeVar

from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger("workshop")
logging.basicConfig(
    level=logging.INFO,
    format="\033[90m%(asctime)s\033[0m \033[94m%(name)s\033[0m \033[32m%(levelname)-8s\033[0m %(message)s",
    datefmt="%H:%M:%S",
    stream=sys.stdout,
)

_token = os.getenv("LOGFIRE_TOKEN", "")
_logfire = None

if _token:
    try:
        import logfire

        logfire.configure(service_name="workshop-code-examples")
        logfire.instrument_openai()
        logfire.instrument_openai_agents()
        _logfire = logfire.with_settings(tags=["code_examples"])
        logger.info("Logfire tracing enabled for this example")
    except Exception as e:
        logger.warning(f"Logfire setup skipped: {e}")
else:
    logger.info("Logfire tracing disabled (no LOGFIRE_TOKEN in .env)")


T = TypeVar("T")


@contextmanager
def example_run(example_name: str):
    span = (
        _logfire.span(
            "code example run",
            example_name=example_name,
            run_group="code_examples",
        )
        if _logfire
        else nullcontext()
    )
    with span:
        logger.info("Starting example: %s", example_name)
        if _logfire:
            _logfire.info(
                "Code example started",
                example_name=example_name,
                run_group="code_examples",
            )
        try:
            yield
        except Exception:
            logger.exception("Example failed: %s", example_name)
            raise
        finally:
            logger.info("Finished example: %s", example_name)
            if _logfire:
                _logfire.info(
                    "Code example finished",
                    example_name=example_name,
                    run_group="code_examples",
                )


async def run_example(example_name: str, awaitable: Awaitable[T]) -> T:
    with example_run(example_name):
        return await awaitable
