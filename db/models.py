from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from .db import Base

class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    provider = Column(String, index=True)
    magnetLink = Column(String, index=True)
    createdAt = Column(DateTime, index=True)
    updatedAt = Column(DateTime, index=True)
    functional = Column(Boolean, index=True)
    tmdbId = Column(String, index=True, nullable=True)
    season = Column(Integer, index=True, nullable=True)
    episode = Column(Integer, index=True, nullable=True)
