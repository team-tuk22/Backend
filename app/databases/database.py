from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
import time
from sqlalchemy.exc import OperationalError

# 이제 모든 설정은 비서 역할을 하는 config.py 파일로부터 가져옵니다.
from app.config import DATABASE_URL

# engine을 한 번만 명확하게 생성합니다.
engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# 데이터베이스 테이블 생성을 위한 함수
def init_db():
    try:
        Base.metadata.create_all(bind=engine)
        print("✅ Created DB tables (if not exist)")
    except Exception as e:
        print(f"❌ Failed to create tables: {e}")