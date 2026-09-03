import os
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

# Railway bergan DATABASE_URL ni oladi, topilmasa lokal SQLite ishlatadi
DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///bot_database.db")

# SQLAlchemy 1.4+ versiyalarida "postgres://" bo'lsa "postgresql://" ga almashtirish shart
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Baza turiga qarab engine sozlanadi
if "sqlite" in DATABASE_URL:
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
else:
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, unique=True, index=True)
    username = Column(String(100), nullable=True)
    full_name = Column(String(150), nullable=True)
    phone_number = Column(String(30), nullable=True)
    is_registered = Column(Boolean, default=False)
    tests_remaining = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.now)

class Block(Base):
    __tablename__ = 'blocks'
    id = Column(Integer, primary_key=True)
    title = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    questions = relationship("Question", back_populates="block", cascade="all, delete-orphan")

class Question(Base):
    __tablename__ = 'questions'
    id = Column(Integer, primary_key=True)
    block_id = Column(Integer, ForeignKey('blocks.id'), nullable=False)
    q_type = Column(String(20), default="mcq") # "mcq" yoki "open"
    text = Column(Text, nullable=False)
    option_a = Column(Text, nullable=True)
    option_b = Column(Text, nullable=True)
    option_c = Column(Text, nullable=True)
    option_d = Column(Text, nullable=True)
    correct_answer = Column(Text, nullable=False)
    
    block = relationship("Block", back_populates="questions")

class UserAnswer(Base):
    __tablename__ = 'user_answers'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, index=True)
    question_id = Column(Integer, ForeignKey('questions.id'))
    user_answer = Column(Text, nullable=True)
    is_correct = Column(Boolean, nullable=True)
    updated_at = Column(DateTime, default=datetime.now)

class TestResult(Base):
    __tablename__ = 'test_results'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, index=True)
    block_id = Column(Integer, nullable=True)
    total_questions = Column(Integer, default=45)
    correct_answers = Column(Integer, default=0)
    wrong_answers = Column(Integer, default=0)
    percentage = Column(Integer, default=0)
    completed_at = Column(DateTime, default=datetime.now)

Base.metadata.create_all(bind=engine)