from sqlalchemy.orm import Session, load_only
from sqlalchemy import func
import uuid
import models, schemas
from typing import Optional, List
from fastapi import Request
import email_scheduler
import datetime

def get_event(db: Session, event_id: uuid.UUID):
    event = db.query(models.Event).get(event_id)
    is_custom_answers_added = event.is_custom_answers_added
    answers = []
    for answer in event.answers:
        if answer.is_custom:
            if is_custom_answers_added:
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
    if event.will_email_admin and event.admin_email != '':
        email_scheduler.add_job(str(db_event.id), event.voting_deadline, event.admin_email, event.question)
    return db_event


def patch_event_admin_email(db: Session, admin_email: str, will_email_admin: bool, event_id: uuid.UUID): # TODO set cron or other to send email
    db_event = db.query(models.Event).get(event_id)
    db_event.will_email_admin = will_email_admin
    db_event.admin_email = admin_email
    db.commit()
    return db_event


def create_vote(db: Session, votes: List[dict], event_id: uuid.UUID, voter_username: str, voter_email: str):
    if not voter_username:
        voter_username = 'anonymous' + uuid.uuid4().hex
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
    is_vote_changeable = event.is_vote_changeable # TODO if same username or email, say u can either change vote or not! CAN'T multiple vote which means see if there is a voter id and answer id or event id already in place
    answers = {}
    for answer in event.answers:
        if not answer.is_custom:
            answers[answer.answer] = answer.id
    rank = 0
    for vote in votes:
        try:
            answer_id = answers[vote['choice']]
        except KeyError:
            if can_write_custom:
                db_answer = models.Answer(answer=vote['choice'], event_id=event_id, is_custom=True)
                db.add(db_answer)
                db.flush()
                db.commit()
                answer_id = db_answer.id
            else:
                return {"error":"cannot add custom"}
        if vote['dates']:
            for date in vote['dates']:
                date_start = datetime.datetime.strptime(date['start'].split(' (')[0], '%a %b %d %Y %H:%M:%S GMT%z') # todo this works for locale en_us, best if client converts locale to timestamp without timezone and sends that value to api
                date_end = datetime.datetime.strptime(date['end'].split(' (')[0], '%a %b %d %Y %H:%M:%S GMT%z')
                db_vote = models.Vote(answer_id=answer_id, voter_id=db_voter.id, rank=rank, date_start=date_start, date_end=date_end)
                db.add(db_vote)
        else:
            db_vote = models.Vote(answer_id=answer_id, voter_id=db_voter.id, rank=rank)
            db.add(db_vote)
        rank += 1
    db.flush()
    db.commit()
    return {"success": 1}


def get_result(db: Session, event_id: uuid.UUID): # TODO pagination?
    rows = db.query(models.Answer.answer, func.count(models.Answer.answer)).join(models.Event).join(models.Vote).filter(models.Event.id==event_id).group_by(models.Answer.answer).all() # todo don't count multiple votes from the same username
    return dict(rows)


def get_voters(db: Session, event_id: uuid.UUID, answer: dict): # TODO pagination?
    voters = db.query(models.Voter.username, models.Vote.date_start, models.Vote.date_end).join(models.Vote).join(models.Answer).filter(models.Answer.event_id==event_id).filter(models.Answer.answer==answer['answer']).all()
    return voters
