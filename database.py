import os
from sqlalchemy import Column, Float, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Database configuration (uses SQLite locally, easily adaptable to Postgres)
SQLALCHEMY_DATABASE_URL = "sqlite:///./govspot.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


class ComplaintModel(Base):
  __tablename__ = "complaints"

  id = Column(Integer, primary_key=True, index=True)
  issue_type = Column(String, index=True)
  description = Column(String)
  latitude = Column(Float)
  longitude = Column(Float)
  severity_score = Column(Integer)
  coi_financial_bleed = Column(Float)
  status = Column(String, default="Pending Analysis")


def init_db():
  Base.metadata.create_all(bind=engine)
  print("Database initialized successfully.")


if __name__ == "__main__":
  init_db()