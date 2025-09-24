# from sqlalchemy import create_engine, text
# from sqlalchemy.orm import sessionmaker, declarative_base
# import os
# from dotenv import load_dotenv
# import time
# from sqlalchemy.exc import OperationalError

# load_dotenv()

# DATABASE_URL = os.getenv("DB_URL")
# MAX_RETRIES = 10
# RETRY_DELAY = 2  # seconds

# engine = None

# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()

# #DB 연결 재시도 함수
# def init_engine_with_retries():
#     global engine
#     for attempt in range(1, MAX_RETRIES + 1):
#         try:
#             engine = create_engine(str(DATABASE_URL), pool_pre_ping=True)
#             with engine.connect() as conn:
#                 #커넥션 테스트
#                 conn.execute(text("SELECT 1"))
#             print(f"✅ Connected to DB (attempt {attempt})")
#             break
#         except OperationalError as e:
#             print(f"⚠️  DB connection failed (attempt {attempt}/{MAX_RETRIES}): {e}")
#             time.sleep(RETRY_DELAY)
#     else:
#         raise RuntimeError("❌ Could not connect to the database after multiple attempts")

# engine = create_engine(DATABASE_URL)
# init_engine_with_retries()
# SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
# Base = declarative_base()

# from app.models.model import Base  # 모델들을 메타데이터에 등록


# def init_db():
#     """
#     Create all tables defined in SQLAlchemy models.
#     """
#     try:
#         Base.metadata.create_all(bind=engine)
#         print("✅ Created DB tables (if not exist)")
#     except Exception as e:
#         print(f"❌ Failed to create tables: {e}")
