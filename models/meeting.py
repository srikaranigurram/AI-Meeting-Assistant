from sqlalchemy import Column, Integer, BigInteger, String, Text, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from database import Base


class Meeting(Base):
    __tablename__ = "meetings"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True)
    title = Column(String(255), nullable=False)
    meeting_date = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    transcript = Column(Text, nullable=False, default="")
    summary = Column(Text, nullable=False, default="")
    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now(), nullable=False)

    user = relationship("User", backref="meetings")
    key_points = relationship("KeyPoint", back_populates="meeting", cascade="all, delete-orphan")
    decisions = relationship("Decision", back_populates="meeting", cascade="all, delete-orphan")
    action_items = relationship("ActionItem", back_populates="meeting", cascade="all, delete-orphan")


class KeyPoint(Base):
    __tablename__ = "key_points"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    meeting_id = Column(BigInteger, ForeignKey("meetings.id", ondelete="CASCADE"), nullable=False, index=True)
    point = Column(Text, nullable=False)

    meeting = relationship("Meeting", back_populates="key_points")


class Decision(Base):
    __tablename__ = "decisions"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    meeting_id = Column(BigInteger, ForeignKey("meetings.id", ondelete="CASCADE"), nullable=False, index=True)
    decision = Column(Text, nullable=False)

    meeting = relationship("Meeting", back_populates="decisions")


class ActionItem(Base):
    __tablename__ = "action_items"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    meeting_id = Column(BigInteger, ForeignKey("meetings.id", ondelete="CASCADE"), nullable=False, index=True)
    task = Column(Text, nullable=False)
    assigned_to = Column(String(255), nullable=True)
    deadline = Column(String(255), nullable=True)
    status = Column(String(50), nullable=False, default="pending")

    meeting = relationship("Meeting", back_populates="action_items")