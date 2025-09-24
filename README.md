# Law Backend (FastAPI + Postgres + Docker)

## 요구사항
- Docker Desktop (Windows/Mac)
- PowerShell(Windows) 또는 Terminal(Mac)

## 빠른 시작 (개발용)
```powershell
# 1) .env 작성
copy .env.example .env
# 2) 빌드 & 기동
docker compose up -d --build
# 3) 상태 확인
docker compose ps
# 4) 앱 헬스/문서
# http://localhost:8000/health  -> {"status":"ok"}
# http://localhost:8000/docs    -> Swagger UI
