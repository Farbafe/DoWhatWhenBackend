from sqlalchemy.orm import Session, load_only
from sqlalchemy import func
import uuid
import models, schemas
from typing import Optional, List
from fastapi import Request


def get_event(db: Session, event_id: uuid.UUID):
    event = db.query(models.Event).get(event_id)
    is_custom_answers_added = event.is_custom_answers_added
    answers = []
    for answer in event.answers:
        if answer.is_custom == True:
            if is_custom_answers_added == True:
                answers.append(answer.answer)
        else:
            answers.append(answer.answer)
    event = event.__dict__
    event['answers'] = answers
    event['admin_email'] = ''
    event['admin_token'] = ''
    return event


def create_event(db: Session, event: schemas.EventCreate, answers: List[str]):
    db_event = models.Event(**event.dict())
    db.add(db_event)
    db.flush()
    db.commit()
    for answer in answers:
        db_answer = models.Answer(answer=answer, event_id=db_event.id)
        db.add(db_answer)
    db.flush()
    db.commit()
    return db_event


def patch_event_admin_email(db: Session, admin_email: str, will_email_admin: bool, event_id: uuid.UUID): # TODO set cron or other to send email
    db_event = db.query(models.Event).get(event_id)
    db_event.will_email_admin = will_email_admin
    db_event.admin_email = admin_email
    db.commit()
    return db_event


def create_vote(db: Session, votes: List[dict], event_id: uuid.UUID, voter_username: str, voter_email: str):
    if voter_email != '':
        db_voter = db.query(models.Voter).filter(models.Voter.email == voter_email).first()
    else:
        db_voter = db.query(models.Voter).filter(models.Voter.username == voter_username).first()
    if not db_voter:
        db_voter = models.Voter(username=voter_username, email=voter_email)
        db.add(db_voter)
        db.flush()
        db.commit()
    event = db.query(models.Event).get(event_id)
    can_write_custom = event.can_write_custom
    is_vote_changeable = event.is_vote_changeable # TODO if same username or email, say u can either change vote or not!
    answers = {}
    for answer in event.answers:
        answers[answer.answer] = answer.id
    rank = 0
    for vote in votes:
        try:
            answer_id = answers[vote['choice']]
        except KeyError:
            if can_write_custom:
                db_answer = models.Answer(answer=vote, event_id=event_id, is_custom=True)
                db.add(db_answer)
                db.flush()
                db.commit()
                answer_id = db_answer.id
            else:
                return {"error":"cannot add custom"}
        db_vote = models.Vote(answer_id=answer_id, voter_id=db_voter.id, rank=rank)
        db.add(db_vote)
        rank += 1
        db.flush()
        db.commit()
    return {"success": 1}


def get_result(db: Session, event_id: uuid.UUID): # TODO pagination?
    rows = db.query(models.Answer.answer, func.count(models.Answer.answer)).join(models.Event).join(models.Vote).filter(models.Event.id==event_id).group_by(models.Answer.answer).all()
    return dict(rows)


def get_voters(db: Session, event_id: uuid.UUID, answer: dict): # TODO pagination?
    voters = db.query(models.Voter.username).join(models.Vote).join(models.Answer).filter(models.Answer.event_id==event_id).filter(models.Answer.answer==answer['answer']).all()
    _voters = []
    for voter in voters:
        _voters.append(voter[0])
    return _voters
