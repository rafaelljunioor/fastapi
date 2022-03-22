from typing import Optional,List
from xmlrpc.client import Boolean
from fastapi import FastAPI , Response,status, HTTPException,Depends
from fastapi.params import Body
from pydantic import BaseModel
from random import randrange
import psycopg2 
from psycopg2.extras import RealDictCursor
import time
from sqlalchemy.orm import Session 
from . import models,schemas
from .database import engine,SessionLocal



models.Base.metadata.create_all(bind=engine)

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

while True:

    try: 
        conn = psycopg2.connect(host='localhost',database='fastapi',user='postgres', password='123456',cursor_factory=RealDictCursor)
        cursor = conn.cursor()
        print("Database Connection was succesfull")
        break
    except Exception as error:
        print ("Connection to database failed")
        print ("Error: ", error)
        time.sleep(2)

my_posts = [
    {"title":"title of post 1","content":"content of post 1","id":1},
    {"title":"title of post 1","content":"content of post 2","id":2}
    ]


def find_post(id):
    for p in my_posts:
        if p["id"] == id:
            return p 

def find_index_post(id):
    for i,p in enumerate(my_posts):
        if p['id'] == id:
            return i

@app.get("/")
def root():
    return {"Hello": "Welcome to my API"}



@app.get("/posts",response_model=List[schemas.Post])
def get_posts(db: Session=Depends(get_db)):
    #cursor.execute("""SELECT * FROM posts""")
    #posts = cursor.fetchall()
    posts = db.query(models.Post).all()
    return  posts

    
@app.post("/posts", status_code=status.HTTP_201_CREATED, response_model=schemas.Post)
def create_posts(post: schemas.PostCreate,db: Session=Depends(get_db)):
    #print(new_post.dict())
    #cursor.execute(""" INSERT INTO posts (title, content, published) VALUES (%s,%s,%s) RETURNING * """,(post.title, post.content, post.published))
    #new_post = cursor.fetchone()
    #conn.commit()

    #new_post= models.Post(title=post.title,content=post.content,published=post.published)
    new_post= models.Post(**post.dict())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)

    return new_post

@app.get("/posts/lastest")
def get_latest_post():
    post = my_posts[len(my_posts)-1]
    return  post

@app.get("/posts/{id}",response_model=schemas.Post)
def get_post(id: int,db: Session=Depends(get_db)):
    #cursor.execute("""SELECT * FROM posts where id = %s""",str(id))
    #post = cursor.fetchone()
    #print(test_post)
    #post = find_post(id)

    post = db.query(models.Post).filter(models.Post.id ==id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id: {id} was not Found.")
    return post


@app.delete("/posts/{id}",status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int,db: Session=Depends(get_db)):

    #cursor.execute("""DELETE FROM posts where id = %s returning *""",str(id))
    #deleted_post = cursor.fetchone()
    #conn.commit()
    #index = find_index_post(id)
    post = db.query(models.Post).filter(models.Post.id==id)
    if post.first() == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"post with id:{id} doesn't exist")
    
    post.delete(synchronize_session=False)
    db.commit()
    
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@app.put("/posts/{id}",response_model=schemas.Post)
def update_post(id: int,updated_post: schemas.PostCreate,db: Session=Depends(get_db)):

    #cursor.execute("""UPDATE posts SET title = %s, content=%s, published=%s WHERE ID =%s RETURNING *""",(post.title, post.content, post.published,id))
    #index = find_index_post(id)
    #updated_post = cursor.fetchone()
    #conn.commit()
    post_query = db.query(models.Post).filter(models.Post.id==id)
    post = post_query.first()

    if post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id:{id} doesn't exist")
    
    post_query.update(updated_post.dict(),synchronize_session=False)
    db.commit()

    return post_query.first()


