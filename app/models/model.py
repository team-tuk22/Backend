from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid
from ..db import Base


class Judgement(Base):
    __tablename__ = "judgements"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    case_name = Column(String, index=True, nullable=False)
    case_number = Column(String, index=True, nullable=False)
    case_date = Column(DateTime, index=True, nullable=False)
    case_result = Column(String, index=True, nullable=False)
    case_court = Column(String, index=True, nullable=False)
    case_court_code = Column(Integer, index=True, nullable=False)
    case_type = Column(String, index=True, nullable=False)
    case_type_code = Column(Integer, index=True, nullable=False)
    case_result_type = Column(String, index=True, nullable=False)
    case_result_decision = Column(String, index=True, nullable=False)
    case_result_summary = Column(Text, nullable=True)
    reference = Column(String, nullable=True)
    reference_case = Column(String, nullable=True)
    case_precedent = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.now, nullable=False)
    updated_at = Column(DateTime, default=datetime.now)
