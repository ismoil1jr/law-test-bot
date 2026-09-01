from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

Base = declarative_base()
engine = create_engine("sqlite:///huquq.db", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)

from sqlalchemy import Column, Integer, String, BigInteger
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(BigInteger, unique=True, nullable=True, index=True)
    username = Column(String, unique=True, nullable=True, index=True)
    tests_limit = Column(Integer, default=5)  # Odatiy qiymat: 5 ta test

class Question(Base):
    __tablename__ = "questions"
    id = Column(Integer, primary_key=True)
    text = Column(Text, nullable=False)
    option_a = Column(String, nullable=False)
    option_b = Column(String, nullable=False)
    option_c = Column(String, nullable=False)
    option_d = Column(String, nullable=False)
    correct_answer = Column(String, nullable=False)

class UserAnswer(Base):
    __tablename__ = "user_answers"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    question_id = Column(Integer, nullable=False)
    selected_option = Column(String, nullable=True)
    is_correct = Column(Boolean, nullable=True)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

class TestResult(Base):
    __tablename__ = "test_results"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    total_questions = Column(Integer, default=30)
    correct_answers = Column(Integer, default=0)
    wrong_answers = Column(Integer, default=0)
    percentage = Column(Integer, default=0)
    completed_at = Column(DateTime, default=datetime.now)

Base.metadata.create_all(engine)