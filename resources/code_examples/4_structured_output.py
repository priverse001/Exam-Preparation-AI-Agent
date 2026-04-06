from __future__ import annotations

import asyncio
import logging

import _logfire_setup

from agents import Agent
from agents import Runner
from pydantic import BaseModel
from pydantic import Field

logger = logging.getLogger("workshop.structured_output")


class CityInfo(BaseModel):
    """Structured information about a city"""

    city: str = Field(description="The city name")
    country: str = Field(description="The country name")
    population: int = Field(description="Population count")
    famous_for: list[str] = Field(description="List of things the city is famous for")
    fun_fact: str = Field(description="An interesting fact")


# Create an agent with structured output
agent = Agent(
    name="City Expert",
    instructions="Provide detailed city information.",
    output_type=CityInfo,  # Force structured output
)


async def main():
    # The response will be a CityInfo object, not text!
    result = await Runner.run(agent, "Tell me about Paris")
    city_data: CityInfo = result.final_output

    logger.info(city_data)
    logger.info("----------------------------------------")
    logger.info(f"{city_data.city}, {city_data.country}")
    logger.info(f"Population: {city_data.population:,}")
    logger.info(f"Famous for: {', '.join(city_data.famous_for)}")
    logger.info(f"Fun fact: {city_data.fun_fact}")


if __name__ == "__main__":
    asyncio.run(_logfire_setup.run_example("4_structured_output", main()))
