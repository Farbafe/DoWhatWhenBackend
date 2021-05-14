from sqlalchemy import Boolean, Column, ForeignKey, String, DateTime, Enum, Table, Integer, PickleType
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import voting_method_enum
import uuid
from database import Base


class Answer(Base):
    __tablename__ = "answers"

    id = Column(Integer, primary_key=True)
    answer = Column(String, index=True)
    is_custom = Column(Boolean, default=False)
    event_id = Column(UUID(as_uuid=True), ForeignKey("events.id"))

    event = relationship("Event", back_populates="answers")


class Voter(Base):
    __tablename__ = "voters"

    id = Column(Integer, primary_key=True)
    username = Column(String, index=True)
    email = Column(String, index=True, nullable=True)


class Event(Base):
    __tablename__ = "events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True)
    question = Column(String, index=True)
    admin_email = Column(String)
    admin_token = Column(String)
    can_write_custom = Column(Boolean, default=False)
    is_voter_anonymous = Column(Boolean, default=True)
    is_vote_changeable = Column(Boolean, default=False)
    is_result_live = Column(Boolean, default=True)
    must_rank_all = Column(Boolean, default=False)
    is_custom_answers_added = Column(Boolean, default=False)
    will_email_admin = Column(Boolean, default=True)
    voting_method = Column(Enum(voting_method_enum.VotingMethod))
    voting_deadline = Column(DateTime)

    answers = relationship("Answer", back_populates="event")


class Vote(Base):
    __tablename__ = "votes"

    id = Column(Integer(), primary_key=True)
    answer_id = Column(Integer, ForeignKey("answers.id"))
    date_start = Column(DateTime)
    date_end = Column(DateTime)
    rank = Column(Integer)
    voter_id = Column(Integer, ForeignKey("voters.id"))

    answer = relationship("Answer", backref="votes")
    voter = relationship("Voter", backref="votes")
