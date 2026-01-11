from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Base, Session, Suggestion, Decision

# TODO: Move to config
DATABASE_URL = "sqlite:///blog_editor.db"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db() -> None:
    Base.metadata.create_all(bind=engine)

def create_session(draft_id: str) -> Session:
    db = SessionLocal()
    try:
        session = Session(draft_id=draft_id)
        db.add(session)
        db.commit()
        db.refresh(session)
        return session
    finally:
        db.close()

def add_suggestions(session_id: int, suggestions_data: list[dict]) -> None:
    db = SessionLocal()
    try:
        for s_data in suggestions_data:
            suggestion = Suggestion(
                session_id=session_id,
                type=s_data["type"],
                location=s_data["location"],
                original_text=s_data["original_text"],
                proposed_text=s_data["proposed_text"],
                reasoning=s_data["reasoning"]
            )
            db.add(suggestion)
        db.commit()
    finally:
        db.close()

def record_decision(session_id: int, suggestion_id: int, action: str) -> None:
    db = SessionLocal()
    try:
        decision = Decision(
            session_id=session_id,
            suggestion_id=suggestion_id,
            action=action
        )
        db.add(decision)
        db.commit()
    finally:
        db.close()
