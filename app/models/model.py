from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid
from app.databases.database import Base


class Judgement(Base):
    __tablename__ = "judgements"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4) # 일련번호

    case_name = Column(String, index=True, nullable=False)                # 사건명
    case_number = Column(String, index=True, nullable=False)              # 사건번호
    case_date = Column(DateTime, index=True, nullable=False)              # 선고일자
    case_result = Column(String, index=True, nullable=False)              # 선고
    case_court = Column(String, index=True)                               # 법원명      
    case_court_code = Column(Integer, index=True)                         # 법원코드
    case_type = Column(String, index=True)                                # 사건종류
    case_type_code = Column(Integer, index=True)                          # 사건종류코드
    case_result_type = Column(String, index=True)                         # 판결유형
    case_result_decision = Column(String, index=True, nullable=False)     # 판결시사항
    case_result_summary = Column(Text, nullable=True)                     # 판결요지
    reference = Column(String, nullable=True)                             # 참조조문
    reference_case = Column(String, nullable=True)                        # 참조판례
    case_precedent = Column(Text, nullable=True)                          # 판례요지

    created_at = Column(DateTime, default=datetime.now, nullable=False)   # 생성일자
    updated_at = Column(DateTime, default=datetime.now)                   # 수정일자 
