from sqlalchemy import Column,Integer,String,DateTime,func
from app.database import Base


class Post(Base):
    __tablename__ = "posts"
    id = Column(Integer,primary_key=True, index=True)
    author_id = Column(Integer, nullable=False)
    title = Column(String(100), nullable=False)
    content = Column(String(1000), nullable=False)
    create_at = Column(DateTime(timezone=True),server_default=func.now())
    status = Column(Integer,default=0)