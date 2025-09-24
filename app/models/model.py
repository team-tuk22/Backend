# app/models/model.py
import uuid
from datetime import datetime, date
from sqlalchemy import Column, String, Date, Text, DateTime, Integer, UniqueConstraint
from app.databases.database import Base

class Judgement(Base):
    __tablename__ = "judgements"

    # UUID → String(36)으로 수정 (SQLite/Postgres 모두 호환)
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    # db에 저장될 때 자동으로 UUID 생성

    case_name = Column(String(255), nullable=False)
    case_number = Column(String(100), nullable=False)
    case_date = Column(Date, nullable=False)  # DateTime →  (data(YYYYMMDD)형태로 저장)

    case_result = Column(String(100), nullable=True)
    case_court = Column(String(100), nullable=True)
    case_court_code = Column(Integer, nullable=True)

    case_type = Column(String(100), nullable=True)
    case_type_code = Column(Integer, nullable=True)

    case_result_type = Column(String(100), nullable=True)
    case_result_decision = Column(String(255), nullable=True)

    case_result_summary = Column(Text, nullable=True)
    reference = Column(Text, nullable=True)
    reference_case = Column(Text, nullable=True)
    case_precedent = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.now, nullable=False)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    # 레코드가 수정될 때 자동으로 업데이트

    # 동일한 사건번호 + 날짜 조합은 중복 저장 방지
    __table_args__ = (
        UniqueConstraint("case_number", "case_date", name="uq_case_num_date"),
    )
