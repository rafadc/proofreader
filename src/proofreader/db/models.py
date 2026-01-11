from datetime import datetime
from typing import Optional
from sqlalchemy import String, Integer, DateTime, ForeignKey, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class Base(DeclarativeBase):
    pass

class Session(Base):
    __tablename__ = "sessions"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    draft_id: Mapped[str] = mapped_column(String, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    suggestions: Mapped[list["Suggestion"]] = relationship(back_populates="session")
    decisions: Mapped[list["Decision"]] = relationship(back_populates="session")

class Suggestion(Base):
    __tablename__ = "suggestions"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    session_id: Mapped[int] = mapped_column(ForeignKey("sessions.id"))
    type: Mapped[str] = mapped_column(String)  # typo, structure, coherence
    location: Mapped[str] = mapped_column(String)
    original_text: Mapped[str] = mapped_column(Text)
    proposed_text: Mapped[str] = mapped_column(Text)
    reasoning: Mapped[str] = mapped_column(Text)
    
    session: Mapped["Session"] = relationship(back_populates="suggestions")
    decision: Mapped[Optional["Decision"]] = relationship(back_populates="suggestion")

class Decision(Base):
    __tablename__ = "decisions"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    session_id: Mapped[int] = mapped_column(ForeignKey("sessions.id"))
    suggestion_id: Mapped[int] = mapped_column(ForeignKey("suggestions.id"))
    action: Mapped[str] = mapped_column(String)  # approve, reject
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    session: Mapped["Session"] = relationship(back_populates="decisions")
    suggestion: Mapped["Suggestion"] = relationship(back_populates="decision")
