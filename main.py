from typing import List
import uuid
from fastapi import Depends, FastAPI, HTTPException, Body, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_login import LoginManager
from fastapi_login.exceptions import InvalidCredentialsException
from sqlalchemy.orm import Session

import crud, models, schemas
import email_scheduler
import os
import bcrypt
from database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

LOGIN_SECRET = os.getenv('FASTAPI_LOGIN_SECRET')

app = FastAPI()

manager = LoginManager(LOGIN_SECRET, token_url='/auth/login')

# origins = [
#     "http://localhost:8080",
#     "http://192.168.1.2:8080",
#     "http://deebremote.duckdns.org:8080",
#     "http://127.0.0.1:8080"
# ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


@app.on_event("startup")
def startup():
    email_scheduler.start_scheduler('sqlite:///email_database.sqlite')

@app.on_event("shutdown")
def shutdown():
    email_scheduler.shutdown_scheduler()


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() # not an error, just pylint


@manager.user_loader
def load_user(email: str):
    fake_db = {"email01@example.com": {"password": bcrypt.hashpw(u"randompassword".encode("utf8"), bcrypt.gensalt()), "username": "user name placeholder"}, "email02@example.com": {"password": bcrypt.hashpw(u"strongerrandompassword".encode("utf8"), bcrypt.gensalt()), "username": "user name placeholder 02"}}
    return fake_db.get(email)


@app.post("/auth/login")
def login(data: OAuth2PasswordRequestForm = Depends()):
    email = data.username
    password = data.password
    user = load_user(email)
    if not user:
        raise InvalidCredentialsException
    if not bcrypt.checkpw(password.encode("utf8"), user['password']):
        raise InvalidCredentialsException
    access_token = manager.create_access_token(data=dict(sub=email))
    return {"access_token": access_token, 'token_type': 'bearer'}


@app.get("/auth/user")
def get_user(user=Depends(manager)):
    return {"user": user}


@app.post("/event", response_model=schemas.Event)
def create_event(event: schemas.EventCreate, answers: List[str], db: Session = Depends(get_db)):
    return crud.create_event(db=db, event=event, answers=answers)


@app.patch("/event/{event_id}/admin", response_model=schemas.Event)
def patch_event_admin_email(event_id: uuid.UUID, admin_email: str = Body(...), will_email_admin: bool = Body(...), db: Session = Depends(get_db)):
    return crud.patch_event_admin_email(db=db, event_id=event_id, admin_email=admin_email, will_email_admin=will_email_admin)


@app.get("/event/{event_id}")
def get_event(event_id: uuid.UUID, db: Session = Depends(get_db)):
    return crud.get_event(db=db, event_id=event_id)


@app.post("/event/{event_id}/vote")
def create_vote(votes: List[dict], event_id: uuid.UUID, db: Session = Depends(get_db), voter_username: str = Body(...), voter_email: str = Body(...)):
    return crud.create_vote(db=db, votes=votes, event_id=event_id, voter_username=voter_username, voter_email=voter_email)


@app.get("/event/{event_id}/result")
def get_result(event_id: uuid.UUID, db: Session = Depends(get_db)):
    return crud.get_result(db=db, event_id=event_id)


@app.post("/event/{event_id}/voters")
def get_voters(event_id: uuid.UUID, answer: dict = Body(...), db: Session = Depends(get_db)):
    return crud.get_voters(db=db, event_id=event_id, answer=answer)
