from typing import List
from sqlalchemy import and_, select
from app.schemas.post import PostCreate, PostId,PostResponse, PostUpdate # 모델을 임포트 해야 메타데이터에 반영됨
from fastapi import Depends, FastAPI,HTTPException
from app.database import get_db, lifsqan,engine
from app.models.post import Post
from sqlalchemy.ext.asyncio import AsyncSession

app = FastAPI(lifespan=lifsqan,
              title="FastAPI CRUD활용",
              description="FastAPI와 MySQL을 연동한 게시판 연습입니다.",
              verpysion="0.1.1",
              redoc_url=None,
              docs_url="/tester/docs")

@app.get("/")
async def root():
    return {"message": "연습입니다."}

@app.get("/ping")
async def ping_db():
    try:
        async with engine.connect() as conn:
            return {"status":"DB connected"}
    except Exception as e:
        return {"status":"DB connetion failed", "error":str(e)}

@app.post("/create",response_model=PostResponse,
          summary="게시물 저장기능",
          description="저장할 자원(title, content)을 인자로 전달하여 저장한다.") # posts게시물 저장
async def create(post:PostCreate,db:AsyncSession=Depends(get_db)):
    # 이미 인자인 post에 저장할 값들이 들어온 상태다.
    # post변수에 있는 값들으 테이블 모델(Post)메 저장하자!
    create_post = Post(title=post.title,content=post.content,author_id=post.author)
    db.add(create_post) # db세션에 위의 값을 등록
    await db.commit() # db에 적용
    await db.refresh(create_post) # db에 적용된 내용과 일치시킨다.(id, create_at,status) 들어옴
    return create_post

@app.get("/get/{id}",response_model=PostResponse,
         summary="게시물 조회",
         description="기본키를 인자로 받아서 게시물을 조회합니다.",
         responses={
            404:{
                "description": "해당 기본키에 맞는 게시물이 없습니다.",
                "content":{
                    "application/json":{
                        "example":{
                            "detail":"찾는 게시물이 없습니다."
                        }
                    }
                }
            }     
        }) # posts게시물 검색(읽기)
async def read_get(id:int,db:AsyncSession =Depends(get_db)):
    query = select(Post).where(and_(Post.id==id,Post.status==0))
    result = await db.execute(query)
    post = result.scalars().one_or_none()
    if not post: # if post is None:
        raise HTTPException(status_code=404,detail="찾는 게시물이 없습니다.")
    return post

@app.get("/list",response_model=List[PostResponse]) # 목록 읽기
async def postlist(db:AsyncSession=Depends(get_db)):
    query = select(Post).where(Post.status==0).order_by(Post.create_at.desc())
    # SQLAlchemy2.0스타일 쿼리
    result = await db.execute(query)
    list = result.scalars().all()
    if list is None: # 만약! 받은 게시물이 없다면 강제 예외 발생
        raise HTTPException(status_code=404,detail="게시물이 없습니다.")
    return list

# posts게시물 수정
@app.put("/edit/{id}",response_model=PostResponse)
async def read_edit(id:int, payload:PostUpdate, db:AsyncSession=Depends(get_db)):
    # 먼저 기본키를 패스 파라미터로 받았으므로 검색부터 하자
    query = select(Post).where(Post.id==id)
    result = await db.execute(query)
    post = result.scalars().one_or_none()
    if post is None:
        raise HTTPException(status_code=404,detail="찾는 게시물이 없습니다.")
    
    if payload.title is not None:
        post.title = payload.title
    if payload.content is not None:
        post.content = payload.content
    
    await db.commit() #DB에 적용
    await db.refresh(post)
    return post

# posts게시물 삭제
"""
@app.delete("/del/{id}")
async def read_del(id:int,db:AsyncSession=Depends(get_db)):
    # 인자로 받은 id와 같은 자원을 검색
    query = select(Post).where(Post.id==id)
    result = await db.execute(query)
    post = result.scalars().one_or_none()
    if post is None:
        raise HTTPException(status_code=404,detail='삭제할 게시물이 없습니다.')
    await db.delete(post)
    await db.commit()
    return {"message":"삭제완료!"}
"""
@app.get("/delete/{id}")
async def read_delete(id:int,db:AsyncSession=Depends(get_db)):
    query = select(Post).where(Post.id==id)
    result = await db.execute(query)
    post = result.scalars().one_or_none()
    if post is None:
        raise HTTPException(status_code=404,detail='찾는 게시물이 없습니다.')
    post.status = 0
    await db.commit()
    await db.refresh(post)
    return {"message":"게시물이 삭제되었습니다."}
    
# DB연결 해보자 - aiomysql , sqlalchemy , pydantic-settings 필요함
# 터미널 창에서
# python -m pip install aiomysql sqlalchemy pydantic-settings
