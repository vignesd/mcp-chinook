
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class HealthCheckOutput(BaseModel):
    """Structured response for the database health check."""

    model_config = ConfigDict(extra="forbid")

    status: Literal["healthy", "unhealthy"]
    database: str
    message: str


class ServerInfoOutput(BaseModel):
    """Structured response containing server metadata."""

    model_config = ConfigDict(extra="forbid")

    server_name: str
    version: str
    transport: str
    database_engine: str
    database_file: str
    tools: list[str] = Field(
        description="Names of tools registered by the server."
    )
