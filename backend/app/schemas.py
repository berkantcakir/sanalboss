from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    email: EmailStr
    name: str


class UserRead(BaseModel):
    id: int
    email: EmailStr
    name: str
    created_at: datetime

    class Config:
        from_attributes = True


class JobCreate(BaseModel):
    title: str
    description: str


class JobRead(BaseModel):
    id: int
    title: str
    description: str
    created_at: datetime

    class Config:
        from_attributes = True


class JobNoteCreate(BaseModel):
    note: str


class JobNoteRead(BaseModel):
    id: int
    note: str
    created_at: datetime

    class Config:
        from_attributes = True


class JobDetail(JobRead):
    notes: List[JobNoteRead] = []


class PlanRequest(BaseModel):
    start_hour: int
    end_hour: int
    focus_hours: Optional[int] = None


class PlanItem(BaseModel):
    start_time: str
    end_time: str
    task: str


class PlanResponse(BaseModel):
    job_id: int
    plan: List[PlanItem]
    message: str
