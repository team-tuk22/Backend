import uuid
from datetime import datetime, date
from sqlalchemy import Column, String, Date, Text, DateTime, Integer, UniqueConstraint
from app.db import Base

class Judgement(Base):
    __tablename__ = "judgements"


    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4) # 일련번호

    case_name = Column(String(255), index=True, nullable=False)           # 사건명
    case_number = Column(String(100), index=True, nullable=False)         # 사건번호
    case_date = Column(DateTime, index=True, nullable=False)              # 선고일자
    case_result = Column(String(100), index=True, nullable=False)         # 선고
    case_court = Column(String(100), index=True)                          # 법원명      
    case_court_code = Column(Integer, index=True)                         # 법원코드
    case_type = Column(String(100), index=True)                           # 사건종류
    case_type_code = Column(Integer, index=True)                          # 사건종류코드
    case_result_type = Column(String(100), index=True)                    # 판결유형
    case_result_decision = Column(String, index=True)                     # 판결시사항
    case_result_summary = Column(Text, nullable=True)                     # 판결요지
    reference = Column(String, nullable=True)                             # 참조조문
    reference_case = Column(Text, nullable=True)                          # 참조판례
    case_precedent = Column(Text, nullable=True)                          # 판례요지

    created_at = Column(DateTime, default=datetime.now, nullable=False)   # 생성일자
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)  # 수정일자 
    
    # 동일한 사건번호 + 날짜 조합은 중복 저장 방지
    __table_args__ = (
        UniqueConstraint("case_number", "case_date", name="uq_case_num_date"),
    )