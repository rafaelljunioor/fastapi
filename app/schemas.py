
from pydantic import BaseModel
from datetime import datetime

class PostBase(BaseModel): 
    title: str
    content: str
    published: bool = True 
   

class CreatePost(BaseModel): 
    title: str
    content: str
    published: bool = True 

class UpdatePost(BaseModel): 
    title: str
    content: str
    published: bool = True  

class PostCreate(PostBase):
    pass

class Post(PostBase):
    id: int
    #content: str  
    #title: str
    #published: bool
    created_at: datetime

    class Config:
        orm_mode = True

