
from mcp.types import ToolAnnotations

# ---------------------------------------------------------
# Read operations
# ---------------------------------------------------------

READ = ToolAnnotations(
    read_only_hint=True,
    destructive_hint=False,
    idempotent_hint=True,
    open_world_hint=False,
)


# ---------------------------------------------------------
# Create operations
# ---------------------------------------------------------

CREATE = ToolAnnotations(
    read_only_hint=False,
    destructive_hint=False,
    idempotent_hint=False,
    open_world_hint=False,
)


# ---------------------------------------------------------
# Update operations
# ---------------------------------------------------------

UPDATE = ToolAnnotations(
    read_only_hint=False,
    destructive_hint=False,
    idempotent_hint=True,
    open_world_hint=False,
)


# ---------------------------------------------------------
# Delete operations
# ---------------------------------------------------------

DELETE = ToolAnnotations(
    read_only_hint=False,
    destructive_hint=True,
    idempotent_hint=True,
    open_world_hint=False,
)


# ---------------------------------------------------------
# General write operations
# ---------------------------------------------------------

WRITE = ToolAnnotations(
    read_only_hint=False,
    destructive_hint=False,
    idempotent_hint=False,
    open_world_hint=False,
)


# ---------------------------------------------------------
# Destructive write operations
# ---------------------------------------------------------

DESTRUCTIVE_WRITE = ToolAnnotations(
    read_only_hint=False,
    destructive_hint=True,
    idempotent_hint=False,
    open_world_hint=False,
)


# ---------------------------------------------------------
# Idempotent write operations
# ---------------------------------------------------------

IDEMPOTENT_WRITE = ToolAnnotations(
    read_only_hint=False,
    destructive_hint=False,
    idempotent_hint=True,
    open_world_hint=False,
)


# ---------------------------------------------------------
# External read operations
# ---------------------------------------------------------

EXTERNAL_READ = ToolAnnotations(
    read_only_hint=True,
    destructive_hint=False,
    idempotent_hint=True,
    open_world_hint=True,
)


# ---------------------------------------------------------
# External write operations
# ---------------------------------------------------------

EXTERNAL_WRITE = ToolAnnotations(
    read_only_hint=False,
    destructive_hint=False,
    idempotent_hint=False,
    open_world_hint=True,
)


# ---------------------------------------------------------
# External destructive operations
# ---------------------------------------------------------

EXTERNAL_DESTRUCTIVE_WRITE = ToolAnnotations(
    read_only_hint=False,
    destructive_hint=True,
    idempotent_hint=False,
    open_world_hint=True,
)
