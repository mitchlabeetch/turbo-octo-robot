"""
Schemas package — re-exports all Pydantic schemas for backward compatibility.
"""

# Original schemas (CRM, Auth, Documents)
from app.schemas.core import *  # noqa: F401,F403

# Deal management schemas
from app.schemas.deals import *  # noqa: F401,F403

# Financial schemas
from app.schemas.finance import *  # noqa: F401,F403

# Project schemas
from app.schemas.projects import *  # noqa: F401,F403
