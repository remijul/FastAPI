from enum import Enum
from fastapi import Path
from typing import Optional

class APIVersion(str, Enum):
    """Supported API versions"""
    V1 = "v1"
    V2 = "v2"