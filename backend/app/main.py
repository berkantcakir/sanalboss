from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from .ai import LLMAdapter
from .models import Base, Job, JobPlan

DATABASE_URL = "sqlite:///./app.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

app = FastAPI(title="Sanalboss AI")
adapter = LLMAdapter()


class PlanStepSchema(BaseModel):
    title: str
    detail: str


class PlanRequest(BaseModel):
    job_title: str = Field(..., min_length=1)
    job_description: str = Field(..., min_length=1)


class PlanFeedbackRequest(BaseModel):
    feedback: str = Field(..., min_length=1)
    failure_reason: Optional[str] = None


class JobPlanResponse(BaseModel):
    job_id: int
    plan_steps: List[PlanStepSchema]
    motivation_message: str
    feedback: Optional[str]
    failure_reason: Optional[str]
    created_at: datetime


def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.on_event("startup")
def startup() -> None:
    Base.metadata.create_all(bind=engine)


@app.post("/jobs", response_model=JobPlanResponse)
def create_job_plan(payload: PlanRequest, db: Session = Depends(get_db)) -> JobPlanResponse:
    job = Job(title=payload.job_title, description=payload.job_description)
    db.add(job)
    db.commit()
    db.refresh(job)

    response = adapter.generate_plan(
        job_title=job.title,
        job_description=job.description,
    )
    plan = JobPlan(
        job_id=job.id,
        plan=[step.__dict__ for step in response.plan_steps],
        motivation_message=response.motivation_message,
    )
    db.add(plan)
    db.commit()
    db.refresh(plan)
    return JobPlanResponse(
        job_id=job.id,
        plan_steps=[PlanStepSchema(**step) for step in plan.plan],
        motivation_message=plan.motivation_message,
        feedback=plan.feedback,
        failure_reason=plan.failure_reason,
        created_at=plan.created_at,
    )


@app.post("/jobs/{job_id}/ai-plan", response_model=JobPlanResponse)
def generate_job_plan(
    job_id: int,
    payload: PlanRequest,
    db: Session = Depends(get_db),
) -> JobPlanResponse:
    job = db.get(Job, job_id)
    if job is None:
        job = Job(id=job_id, title=payload.job_title, description=payload.job_description)
        db.add(job)
        db.commit()
        db.refresh(job)
    else:
        job.title = payload.job_title
        job.description = payload.job_description
        db.commit()

    response = adapter.generate_plan(
        job_title=job.title,
        job_description=job.description,
    )
    plan = JobPlan(
        job_id=job.id,
        plan=[step.__dict__ for step in response.plan_steps],
        motivation_message=response.motivation_message,
    )
    db.add(plan)
    db.commit()
    db.refresh(plan)
    return JobPlanResponse(
        job_id=job.id,
        plan_steps=[PlanStepSchema(**step) for step in plan.plan],
        motivation_message=plan.motivation_message,
        feedback=plan.feedback,
        failure_reason=plan.failure_reason,
        created_at=plan.created_at,
    )


@app.post("/jobs/{job_id}/ai-plan/feedback", response_model=JobPlanResponse)
def refine_job_plan(
    job_id: int,
    payload: PlanFeedbackRequest,
    db: Session = Depends(get_db),
) -> JobPlanResponse:
    job = db.get(Job, job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")

    response = adapter.generate_plan(
        job_title=job.title,
        job_description=job.description,
        feedback=payload.feedback,
        failure_reason=payload.failure_reason,
    )
    plan = JobPlan(
        job_id=job.id,
        plan=[step.__dict__ for step in response.plan_steps],
        motivation_message=response.motivation_message,
        feedback=payload.feedback,
        failure_reason=payload.failure_reason,
    )
    db.add(plan)
    db.commit()
    db.refresh(plan)
    return JobPlanResponse(
        job_id=job.id,
        plan_steps=[PlanStepSchema(**step) for step in plan.plan],
        motivation_message=plan.motivation_message,
        feedback=plan.feedback,
        failure_reason=plan.failure_reason,
        created_at=plan.created_at,
    )


@app.get("/jobs/{job_id}/ai-plan", response_model=JobPlanResponse)
def get_latest_plan(job_id: int, db: Session = Depends(get_db)) -> JobPlanResponse:
    plan = (
        db.query(JobPlan)
        .filter(JobPlan.job_id == job_id)
        .order_by(JobPlan.created_at.desc())
        .first()
    )
    if plan is None:
        raise HTTPException(status_code=404, detail="Plan not found")
    return JobPlanResponse(
        job_id=plan.job_id,
        plan_steps=[PlanStepSchema(**step) for step in plan.plan],
        motivation_message=plan.motivation_message,
        feedback=plan.feedback,
        failure_reason=plan.failure_reason,
        created_at=plan.created_at,
    )
