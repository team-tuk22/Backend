import os
from typing import Iterable, List, Dict, Any
from datetime import datetime

from opensearchpy import OpenSearch
from opensearchpy.helpers import bulk

from app.models.model import Judgement
from app.db import SessionLocal


INDEX_NAME = os.getenv("OPENSEARCH_INDEX", "law")

client_os = OpenSearch(
    hosts=[{"host": os.getenv("OPENSEARCH_HOST", "opensearch"), "port": int(os.getenv("OPENSEARCH_PORT", "9200"))}],
    http_auth=(os.getenv("OPENSEARCH_USER", "admin"), os.getenv("OPENSEARCH_PASSWORD", "admin")),
    use_ssl=bool(int(os.getenv("OPENSEARCH_SSL", "0"))),
    verify_certs=False,
)


def ensure_index() -> None:
    exists = client_os.indices.exists(index=INDEX_NAME)
    if exists:
        return

    body = {
        "settings": {
            "index": {
                "knn": True
            },
            "analysis": {
                "analyzer": {
                    "korean_ngram": {
                        "type": "custom",
                        "tokenizer": "standard",
                        "filter": ["lowercase", "korean_ngram_filter"]
                    }
                },
                "filter": {
                    "korean_ngram_filter": {
                        "type": "ngram",
                        "min_gram": 2,
                        "max_gram": 3,
                        "token_chars": ["letter", "digit"]
                    }
                }
            }
        },
        "mappings": {
            "properties": {
                "id": {"type": "keyword"},
                "case_name": {
                    "type": "text",
                    "analyzer": "korean_ngram",
                    "search_analyzer": "standard",
                    "fields": {
                        "keyword": {"type": "keyword"}
                    }
                },
                "case_number": {"type": "keyword"},
                "case_date": {"type": "date", "format": "strict_date_optional_time||epoch_millis"},
                "case_result": {"type": "keyword"},
                "case_court": {"type": "keyword"},
                "case_type": {"type": "keyword"},
                "case_result_type": {"type": "keyword"},
                "case_result_decision": {
                    "type": "text",
                    "analyzer": "korean_ngram",
                    "search_analyzer": "standard"
                },
                "case_result_summary": {
                    "type": "text",
                    "analyzer": "korean_ngram",
                    "search_analyzer": "standard"
                },
                "case_precedent": {
                    "type": "text",
                    "analyzer": "korean_ngram",
                    "search_analyzer": "standard"
                },
                "reference": {"type": "text"},
                "reference_case": {"type": "text"},
                # 추후 임베딩 검색을 추가하려면 다음 필드 사용
                # "embedding": {"type": "knn_vector", "dimension": 1536}
            }
        }
    }
    client_os.indices.create(index=INDEX_NAME, body=body)


def _serialize_judgement(doc: Judgement) -> Dict[str, Any]:
    return {
        "id": str(doc.id),
        "case_name": doc.case_name,
        "case_number": doc.case_number,
        "case_date": doc.case_date.isoformat() if isinstance(doc.case_date, datetime) else str(doc.case_date) if doc.case_date else None,
        "case_result": doc.case_result,
        "case_court": doc.case_court,
        "case_type": doc.case_type,
        "case_result_type": doc.case_result_type,
        "case_result_decision": doc.case_result_decision,
        "case_result_summary": doc.case_result_summary,
        "case_precedent": doc.case_precedent,
        "reference": doc.reference,
        "reference_case": doc.reference_case,
    }


def _iter_bulk_actions(docs: Iterable[Judgement]) -> Iterable[Dict[str, Any]]:
    for d in docs:
        yield {
            "_op_type": "index",
            "_index": INDEX_NAME,
            "_id": str(d.id),
            "_source": _serialize_judgement(d),
        }


def index_all_judgements(batch_size: int = 1000) -> Dict[str, Any]:
    ensure_index()

    indexed = 0
    with SessionLocal() as db:
        # 큰 테이블일 수 있으므로 배치로 처리
        offset = 0
        while True:
            rows: List[Judgement] = (
                db.query(Judgement)
                .order_by(Judgement.created_at)
                .offset(offset)
                .limit(batch_size)
                .all()
            )
            if not rows:
                break

            success, errors = bulk(client_os, _iter_bulk_actions(rows))
            indexed += int(success or 0)
            offset += batch_size

            if errors:
                # bulk가 일부 실패하면 오류 객체가 반환될 수 있음
                # 운영 환경에서는 로깅/알림 필요
                pass

    return {"indexed": indexed, "index": INDEX_NAME}


def index_single_judgement(judgement_id: str) -> Dict[str, Any]:
    ensure_index()
    with SessionLocal() as db:
        doc: Judgement | None = db.query(Judgement).filter(Judgement.id == judgement_id).first()
        if not doc:
            return {"indexed": 0, "detail": "not_found"}
        payload = _serialize_judgement(doc)
        client_os.index(index=INDEX_NAME, id=str(doc.id), body=payload)
        return {"indexed": 1, "id": str(doc.id)}


def get_index_doc_count() -> int:
    """인덱스에 있는 문서 개수를 반환합니다."""
    if not client_os.indices.exists(index=INDEX_NAME):
        return 0
    try:
        stats = client_os.count(index=INDEX_NAME)
        return int(stats.get("count", 0) or 0)
    except Exception as e:
        print(f"⚠️  인덱스 문서 개수 확인 중 오류: {e}")
        return 0


def search_by_keyword(keyword: str, limit: int = 10, offset: int = 0) -> Dict[str, Any]:
    if not keyword:
        return {"query": keyword, "limit": limit, "offset": offset, "total": 0, "items": []}

    ensure_index()
    
    # 인덱스가 비어있으면 자동으로 인덱싱 시도
    doc_count = get_index_doc_count()
    if doc_count == 0:
        print(f"⚠️  OpenSearch 인덱스가 비어있습니다. 인덱싱을 시작합니다...")
        try:
            result = index_all_judgements()
            print(f"✅ 인덱싱 완료: {result.get('indexed', 0)}개 문서")
        except Exception as e:
            print(f"❌ 인덱싱 중 오류 발생: {e}")
            import traceback
            traceback.print_exc()

    # 자연어 질문에서 키워드 추출 (간단한 방식: 2글자 이상 단어 추출)
    import re
    # 한글, 숫자, 영문으로 구성된 2글자 이상 단어 추출
    keywords = re.findall(r'[가-힣a-zA-Z0-9]{2,}', keyword)
    if not keywords:
        keywords = [keyword]
    
    # 검색 쿼리 구성: 여러 키워드를 OR 조건으로 검색
    should_clauses = []
    
    # 각 키워드에 대해 multi_match 쿼리 생성
    for kw in keywords:
        should_clauses.extend([
            {
                "multi_match": {
                    "query": kw,
                    "fields": [
                        "case_name^3",
                        "case_result_decision^2",
                        "case_result_summary^1.5",
                        "case_precedent^1",
                    ],
                    "type": "best_fields",
                    "operator": "or",
                }
            },
            {
                "match_phrase": {
                    "case_name": {
                        "query": kw,
                        "boost": 2.0
                    }
                }
            },
            {
                "match_phrase": {
                    "case_result_decision": {
                        "query": kw,
                        "boost": 1.5
                    }
                }
            }
        ])
    
    # 전체 질문도 검색에 포함
    should_clauses.append({
        "multi_match": {
            "query": keyword,
            "fields": [
                "case_name^2",
                "case_result_decision^1.5",
                "case_result_summary^1",
                "case_precedent^1",
            ],
            "type": "best_fields",
            "operator": "or",
        }
    })

    body = {
        "from": offset,
        "size": limit,
        "query": {
            "bool": {
                "should": should_clauses,
                "minimum_should_match": 1
            }
        },
        "_source": [
            "id", "case_name", "case_number", "case_date", "case_result",
            "case_court", "case_type", "case_result_type", "case_result_decision",
            "case_result_summary", "case_precedent", "reference", "reference_case"
        ],
    }

    try:
        # 디버깅: 실제 검색 쿼리 로그
        print(f"🔍 검색 쿼리: '{keyword}' (추출된 키워드: {keywords}, 인덱스: {INDEX_NAME}, 문서 수: {get_index_doc_count()})")
        
        resp = client_os.search(index=INDEX_NAME, body=body)
        hits = resp.get("hits", {})
        total_val = hits.get("total", {}).get("value") if isinstance(hits.get("total"), dict) else hits.get("total", 0)
        
        # 디버깅: 첫 번째 문서 샘플 확인
        if total_val == 0 and get_index_doc_count() > 0:
            # 샘플 문서 하나 가져와서 확인
            sample_resp = client_os.search(index=INDEX_NAME, body={"size": 1})
            if sample_resp.get("hits", {}).get("hits"):
                sample = sample_resp["hits"]["hits"][0]["_source"]
                print(f"📄 샘플 문서: case_name='{sample.get('case_name', '')[:50]}...'")
        
        items: List[Dict[str, Any]] = []
        for h in hits.get("hits", []):
            src = h.get("_source", {})
            items.append({
                "id": src.get("id") or h.get("_id"),
                "case_name": src.get("case_name"),
                "case_number": src.get("case_number"),
                "case_date": src.get("case_date"),
                "case_result": src.get("case_result"),
                "case_court": src.get("case_court"),
                "case_type": src.get("case_type"),
                "case_result_type": src.get("case_result_type"),
                "case_result_decision": src.get("case_result_decision"),
                "case_result_summary": src.get("case_result_summary"),
                "case_precedent": src.get("case_precedent"),
                "reference": src.get("reference"),
                "reference_case": src.get("reference_case"),
                "score": h.get("_score"),
            })

        print(f"🔍 검색 결과: '{keyword}' -> {int(total_val or 0)}개 문서 발견")
        return {
            "query": keyword,
            "limit": limit,
            "offset": offset,
            "total": int(total_val or 0),
            "items": items,
        }
    except Exception as e:
        print(f"❌ OpenSearch 검색 오류: {e}")
        import traceback
        traceback.print_exc()
        raise
