from __future__ import annotations

from pydantic import BaseModel, Field


class SearchRequest(BaseModel):
    q: str = Field("", description="검색어")
    limit: int = Field(10, ge=1, le=100)
    offset: int = Field(0, ge=0)


class SearchResponseItem(BaseModel):
    id: str
    case_name: str | None = None  # 사건명
    case_number: str | None = None  # 사건번호
    case_date: str | None = None  # 선고일자
    case_result: str | None = None  # 선고 (예: 기각, 인용 등)
    case_court: str | None = None  # 법원명
    case_type: str | None = None  # 사건종류
    case_result_type: str | None = None  # 판결유형
    case_result_decision: str | None = None  # 판결시사항
    case_result_summary: str | None = None  # 판결요지
    case_precedent: str | None = None  # 판례요지
    reference: str | None = None  # 참조조문
    reference_case: str | None = None  # 참조판례
    score: float | None = None  # 검색 점수


class SearchResponse(BaseModel):
    query: str
    limit: int
    offset: int
    total: int
    items: list[SearchResponseItem]


