from sqlalchemy.orm import Session

from . import models, schemas


def create_user(db: Session, user: schemas.UserCreate) -> models.User:
    db_user = models.User(email=user.email, name=user.name)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def create_job(db: Session, user_id: int, job: schemas.JobCreate) -> models.Job:
    db_job = models.Job(title=job.title, description=job.description, owner_id=user_id)
    db.add(db_job)
    db.commit()
    db.refresh(db_job)
    return db_job


def create_job_note(db: Session, job_id: int, note: schemas.JobNoteCreate) -> models.JobNote:
    db_note = models.JobNote(job_id=job_id, note=note.note)
    db.add(db_note)
    db.commit()
    db.refresh(db_note)
    return db_note


def get_user_jobs(db: Session, user_id: int):
    return db.query(models.Job).filter(models.Job.owner_id == user_id).all()


def get_job(db: Session, job_id: int):
    return db.query(models.Job).filter(models.Job.id == job_id).first()


def get_job_notes(db: Session, job_id: int):
    return db.query(models.JobNote).filter(models.JobNote.job_id == job_id).all()
