# app/models.py

import uuid
from sqlalchemy import Column, String, Integer, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()


def new_uuid():
    return str(uuid.uuid4())


# ----------------------------
# USERS TABLE
# ----------------------------

class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=new_uuid)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    target_role = Column(String, nullable=True)

    resumes = relationship("Resume", back_populates="user")
    chats = relationship("ChatHistory", back_populates="user")


# ----------------------------
# RESUMES TABLE
# ----------------------------

class Resume(Base):
    __tablename__ = "resumes"

    id = Column(String(36), primary_key=True, default=new_uuid)
    user_id = Column(String(36), ForeignKey("users.id"))
    raw_text = Column(Text, nullable=False)

    original_parsed_data = Column(JSON)
    improved_resume_data = Column(JSON)

    user = relationship("User", back_populates="resumes")
    analytics = relationship("ResumeAnalytics", back_populates="resume")
    interview = relationship("InterviewPrep", back_populates="resume")


# ----------------------------
# RESUME ANALYTICS TABLE
# ----------------------------

class ResumeAnalytics(Base):
    __tablename__ = "resume_analytics"

    id = Column(String(36), primary_key=True, default=new_uuid)
    resume_id = Column(String(36), ForeignKey("resumes.id"))

    ats_score = Column(Integer)
    ats_breakdown = Column(JSON)
    skill_gaps = Column(JSON)

    resume = relationship("Resume", back_populates="analytics")


# ----------------------------
# INTERVIEW PREP TABLE
# ----------------------------

class InterviewPrep(Base):
    __tablename__ = "interview_prep"

    id = Column(String(36), primary_key=True, default=new_uuid)
    resume_id = Column(String(36), ForeignKey("resumes.id"))

    questions_data = Column(JSON)

    resume = relationship("Resume", back_populates="interview")


# ----------------------------
# CHAT HISTORY TABLE
# ----------------------------

class ChatHistory(Base):
    __tablename__ = "chat_history"

    id = Column(String(36), primary_key=True, default=new_uuid)
    user_id = Column(String(36), ForeignKey("users.id"))

    role = Column(String)  # user / assistant
    message = Column(Text)

    user = relationship("User", back_populates="chats")
