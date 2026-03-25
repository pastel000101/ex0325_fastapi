from datetime import datetime
from pydantic import BaseModel

class PostCreate(BaseModel):
    title: str
    content: str
    author: str
    # 나머지는 기본값으로 처리됨

class PostResponse(BaseModel): # 응답객체
    id:int
    title:str
    content:str
    author_id:int
    create_at:datetime
    # ORM객체(Post)로부터 데이터를 가져오도록 함!
    # model_config = ConfigDict(from_attributes=True)
    model_config = {
        "from_attributes":True
    }
    
class PostId(BaseModel):
    id:int

# 수정할 때 사용하는 객체
class PostUpdate(BaseModel):
    title:str
    content:str