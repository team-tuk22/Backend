
from fastapi import APIRouter, Query
from sqlalchemy.orm import Session
from app.utils.crawl import fetch_law_data, save_law_data_to_db, law_data_list

@router.post("/judgement")
def get_judgement(header : str, page = int):
    id_list = law_data_list(header, page)

    results = []
    count = 0
    
    for id in id_list:
        data = fetch_law_data(str(id))
        save_data = save_law_data_to_db(data)
        
        if save_data.get("saved"):
            count += 1
        
        p = data.get("PrecService") if data else None
        results.append({
            "판례일련번호": id, 
            "사건명": p.get("사건명") if p else None,
            "저장상태": "성공" if save_data.get("saved") else "실패"
        })
    
    results.append(f"{len(id_list)}건 중 {count}건 저장됨")
    return results