from fastapi import APIRouter, Query
from fastapi import HTTPException

from app.services.search import (
    ensure_index,
    index_all_judgements,
    search_by_keyword,
)
from app.schemas.search import SearchRequest, SearchResponse, SearchResponseItem


router = APIRouter(prefix="/search", tags=["search"])


@router.post("/index")
def reindex_all():
    try:
        ensure_index()
        result = index_all_judgements()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("")
def search_get(q: str = Query("", min_length=0), limit: int = 10, offset: int = 0) -> SearchResponse:
    try:
        result = search_by_keyword(q, limit=limit, offset=offset)
        return SearchResponse(
            query=result["query"],
            limit=result["limit"],
            offset=result["offset"],
            total=result["total"],
            items=[
                SearchResponseItem(
                    id=item["id"],
                    case_name=item.get("case_name"),
                    case_number=item.get("case_number"),
                    case_date=item.get("case_date"),
                    case_result=item.get("case_result"),
                    case_court=item.get("case_court"),
                    case_type=item.get("case_type"),
                    case_result_type=item.get("case_result_type"),
                    case_result_decision=item.get("case_result_decision"),
                    case_result_summary=item.get("case_result_summary"),
                    case_precedent=item.get("case_precedent"),
                    reference=item.get("reference"),
                    reference_case=item.get("reference_case"),
                    score=item.get("score"),
                )
                for item in result["items"]
            ],
        )
    except Exception as e:
        import traceback
        error_detail = f"{str(e)}\n{traceback.format_exc()}"
        print(f"❌ 검색 오류: {error_detail}")
        raise HTTPException(status_code=500, detail=f"검색 중 오류가 발생했습니다: {str(e)}")


@router.post("")
def search_post(request: SearchRequest) -> SearchResponse:
    try:
        result = search_by_keyword(request.q, limit=request.limit, offset=request.offset)
        return SearchResponse(
            query=result["query"],
            limit=result["limit"],
            offset=result["offset"],
            total=result["total"],
            items=[
                SearchResponseItem(
                    id=item["id"],
                    case_name=item.get("case_name"),
                    case_number=item.get("case_number"),
                    case_date=item.get("case_date"),
                    case_result=item.get("case_result"),
                    case_court=item.get("case_court"),
                    case_type=item.get("case_type"),
                    case_result_type=item.get("case_result_type"),
                    case_result_decision=item.get("case_result_decision"),
                    case_result_summary=item.get("case_result_summary"),
                    case_precedent=item.get("case_precedent"),
                    reference=item.get("reference"),
                    reference_case=item.get("reference_case"),
                    score=item.get("score"),
                )
                for item in result["items"]
            ],
        )
    except Exception as e:
        import traceback
        error_detail = f"{str(e)}\n{traceback.format_exc()}"
        print(f"❌ 검색 오류: {error_detail}")
        raise HTTPException(status_code=500, detail=f"검색 중 오류가 발생했습니다: {str(e)}")

