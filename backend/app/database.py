from contextlib import asynccontextmanager
from typing import AsyncGenerator
from fastapi import FastAPI
from sqlalchemy.orm import declarative_base
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.core.config import config
import logging
import asyncio



engine = create_async_engine(
    config.db_url,
    pool_pre_ping=True # 연결 전에 ping시도 후 연결 유지 여부 판단
    )

# Async 세션 팩토리(세션 생성기)
AsyncSessionLocal = async_sessionmaker(bind=engine,expire_on_commit=False)

Base= declarative_base()

async def get_db() -> AsyncGenerator[AsyncSession,None]:
    async with AsyncSessionLocal() as session:
        yield session
# 위의 with구문으로 커넥션 생명주기가 자동으로 관리되도록 지정되었고
# 모든 사용이 끝나면 자동으로 close되도록 한다.

logger = logging.getLogger("uvicorn.error")
MAX_RETRIES = 10

@asynccontextmanager
async def lifsqan(app: FastAPI):
    # MySQL 이 준비될 때까지 재시도하는 반복문
    for attempt in range(1,MAX_RETRIES+1):
        try:
            # 프로그램이 시작될 때 테이블이 없다면 생성이되도록 하자
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
                # 비동기엔진에서 동기DDL(create_all) 등 실행 할 때 run_sync가 사용됨
            logger.info("DB연결 성공")
            break # 반복문 탈출
        except Exception as e:
            logger.info("DB연결 실패")
            if attempt == MAX_RETRIES:
                logger.error("DB연결 최대 재시도 초과, 프로그램 종료!")
                raise
            await asyncio.sleep(3) # 3초대기
    yield
    await engine.dispose() # 종료시 엔진 리소스를 모두 닫아준다(정리)