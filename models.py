from pydantic import BaseModel
from enum import Enum
from typing import Optional


class CaseStatus(str, Enum):
    open = "open"
    assigned = "assigned"
    closed = "closed"


class Paramedic(BaseModel):
    id: str
    name: str
    phone: str


class Case(BaseModel):
    id: str
    patient_name: str
    patient_phone: str
    status: CaseStatus = CaseStatus.open
    paramedic_id: Optional[str] = None
    proxy_number: Optional[str] = None
