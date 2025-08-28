from fastapi import APIRouter, Query, HTTPException
from pydantic import BaseModel
from typing import Optional
from app.utils.crawl import fetch_law_data, save_law_data_to_db


router = APIRouter()

@router.get("/judgement")
def get_judgement(id: int = Query(..., description="법령 ID")):
    """
    int 타입의 id를 받아 해당 판례 데이터를 크롤링하여 반환하고 DB에 저장합니다.
    """
    result = fetch_law_data(str(id))

    if isinstance(result, dict) and "PrecService" in result:
        saved = save_law_data_to_db(result)
        if saved.get("saved"):
            return {"fetched": result, "db_status": saved}
        else:
            raise HTTPException(status_code=500, detail=saved)
    else:
        raise HTTPException(status_code=400, detail="Invalid response from law.go.kr API")
    