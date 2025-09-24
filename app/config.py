import os
from dotenv import load_dotenv

# .env 파일의 내용을 읽어와서 환경변수로 설정합니다.
load_dotenv()

# 환경변수에서 DATABASE_URL 값을 가져옵니다.
DATABASE_URL = os.getenv("DATABASE_URL")    