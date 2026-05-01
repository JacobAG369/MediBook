# medibook/domain/specialty.py
from sqlalchemy import Column, Integer, String
from medibook.infra.db import Base


class Specialty(Base):
    __tablename__ = "specialties"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(String(255), nullable=True)

    def __repr__(self) -> str:
        return f"<Specialty(id={self.id}, name='{self.name}')>"
