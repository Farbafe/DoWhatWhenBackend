from typing import List, Optional
import datetime
from pydantic import BaseModel
import voting_method_enum
import uuid


class AnswerBase(BaseModel):
    answer: str

class AnswerCreate(AnswerBase):
    pass

class Answer(AnswerBase):
    id: int
    is_custom: bool
    event_id: uuid.UUID

    class Config:
        orm_mode = True


class VoteBase(BaseModel):
    answer_id: int
    date_start: datetime.datetime
    date_end: datetime.datetime

class VoteCreate(VoteBase):
    rank: int
    voter_id: int

class Vote(VoteBase):
    id: int

    class Config:
        orm_mode = True


class VoterBase(BaseModel):
    username: str

class VoterCreate(VoterBase):
    email: Optional[str]

class Voter(VoterBase):
    id: int

    class Config:
        orm_mode = True


class EventBase(BaseModel):
    question: str
    can_write_custom: bool
    is_voter_anonymous: bool
    is_vote_changeable: bool
    is_result_live: bool
    must_rank_all: bool
    is_custom_answers_added: bool
    will_email_admin: bool
    voting_method: voting_method_enum.VotingMethod
    voting_deadline: datetime.datetime

class EventCreate(EventBase):
    admin_email: str
    admin_token: str

class Event(EventBase):
    id: uuid.UUID
    answers: List[Answer]

    class Config:
        orm_mode = True
