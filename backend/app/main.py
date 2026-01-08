from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from . import crud, models, schemas
from .db import Base, engine, get_db

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Sanal Boss API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/users", response_model=schemas.UserRead)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    existing = db.query(models.User).filter(models.User.email == user.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="User already exists")
    return crud.create_user(db, user)


@app.post("/users/{user_id}/jobs", response_model=schemas.JobRead)
def create_job(user_id: int, job: schemas.JobCreate, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return crud.create_job(db, user_id, job)


@app.get("/users/{user_id}/jobs", response_model=list[schemas.JobRead])
def list_jobs(user_id: int, db: Session = Depends(get_db)):
    return crud.get_user_jobs(db, user_id)


@app.get("/jobs/{job_id}", response_model=schemas.JobDetail)
def get_job(job_id: int, db: Session = Depends(get_db)):
    job = crud.get_job(db, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    job.notes = crud.get_job_notes(db, job_id)
    return job


@app.post("/jobs/{job_id}/notes", response_model=schemas.JobNoteRead)
def add_job_note(job_id: int, note: schemas.JobNoteCreate, db: Session = Depends(get_db)):
    job = crud.get_job(db, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return crud.create_job_note(db, job_id, note)


@app.post("/jobs/{job_id}/plan", response_model=schemas.PlanResponse)
def generate_plan(job_id: int, request: schemas.PlanRequest, db: Session = Depends(get_db)):
    job = crud.get_job(db, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    hours = max(request.end_hour - request.start_hour, 1)
    focus = request.focus_hours or hours
    focus = min(focus, hours)

    notes = crud.get_job_notes(db, job_id)
    tasks = [job.description] + [note.note for note in notes]
    steps = []
    segment = max(1, focus // max(len(tasks), 1))
    current = request.start_hour

    for task in tasks:
        end = min(request.end_hour, current + segment)
        steps.append(
            schemas.PlanItem(
                start_time=f"{current}:00",
                end_time=f"{end}:00",
                task=f"{job.title}: {task}",
            )
        )
        current = end
        if current >= request.end_hour:
            break

    if not steps:
        steps.append(
            schemas.PlanItem(
                start_time=f"{request.start_hour}:00",
                end_time=f"{request.end_hour}:00",
                task=f"{job.title}: Odaklanıp ilerleme kaydet.",
            )
        )

    message = (
        "Hedeflerine odaklan. Planı uygula ve gerekirse not ekle, "
        "ben buradayım!"
    )
    return schemas.PlanResponse(job_id=job_id, plan=steps, message=message)
