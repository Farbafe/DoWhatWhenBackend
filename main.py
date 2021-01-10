from typing import List
import uuid
from fastapi import Depends, FastAPI, HTTPException, Body, Request
from sqlalchemy.orm import Session

import crud, models, schemas
from database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() # not an error, just pylint


@app.post("/events/", response_model=schemas.Event)
def create_event(event: schemas.EventCreate, answers: List[schemas.AnswerCreate], db: Session = Depends(get_db)):
    return crud.create_event(db=db, event=event, answers=answers)


@app.get("/events/{event_id}", response_model=schemas.Event)
def get_event(event_id: uuid.UUID, db: Session = Depends(get_db)):
    return crud.get_event(db=db, event_id=event_id)


@app.post("/events/{event_id}/vote")
def create_vote(votes: List[str], event_id: uuid.UUID, db: Session = Depends(get_db), voter_username: str = Body(...), voter_email: str = Body(...)):
    return crud.create_vote(db=db, votes=votes, event_id=event_id, voter_username=voter_username, voter_email=voter_email)


@app.get("/events/{event_id}/result")
def get_result(event_id: uuid.UUID, db: Session = Depends(get_db)):
    return crud.get_result(db=db, event_id=event_id)


@app.post("/events/{event_id}/voters")
def get_voters(event_id: uuid.UUID, answer: dict, db: Session = Depends(get_db)):
    return crud.get_voters(db=db, event_id=event_id, answer=answer)
