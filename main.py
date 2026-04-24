from fastapi import FastAPI, Query, Body, HTTPException
from typing import Optional
from pydantic import BaseModel

app = FastAPI(title="My FastAPI Application")

BLOG_POSTS = [
    {"id": 1, "title": "Hello FastAPI", "content": "This is my first blog post."},
    {"id": 2, "title": "FastAPI is Awesome", "content": "FastAPI makes it easy to build APIs."},
    {"id": 3, "title": "Python is Great", "content": "Python is a versatile programming language."}
]

@app.get("/")
def home():
    return {"message": "Hello, World!"}

class PostBase(BaseModel):
    title: str
    content: Optional[str] = "New post content goes here."

class PostCreate(PostBase):
    pass

class PostUpdate(BaseModel):
    title: str
    content: Optional[str] = None

@app.get("/posts")
def list_posts(query: Optional[str] = Query(default=None, description="Search query for blog posts")):
    if query:
        # results = [post for post in BLOG_POSTS if query.lower() in post["title"].lower()]
        results = []
        for post in BLOG_POSTS:
            if query.lower() in post["title"].lower():
                results.append(post)
        return {"data": results, "query": query}
    else: 
        return {"data": BLOG_POSTS}
    
@app.get("/posts/{post_id}")
def get_post(post_id: int, include_content: Optional[bool] = Query(default=True, description="Include content in the response")):
    for post in BLOG_POSTS:
        if post_id == post["id"]:
            if not include_content:
                return {"id": post["id"], "title": post["title"]}
            return {"data": post}
    return {"error": "Post not found"}

@app.post("/posts")
def create_post(post: PostCreate):
    new_id = (BLOG_POSTS[-1]["id"]+1) if BLOG_POSTS else 1
    new_post = {"id": new_id, "title": post.title, "content": post.content}
    BLOG_POSTS.append(new_post)
    return {"message": "Post created successfully", "data": new_post}

@app.put("/posts/{post_id}")
def update_post(post_id: int, data: PostUpdate):
    for post in BLOG_POSTS:
        if post["id"] == post_id:
            payload = data.model_dump(exclude_unset=True)
            if "title" in payload:
                post["title"] = payload["title"]
            if "content" in payload:
                post["content"] = payload["content"]
            return {"message": "Post updated", "data": post}
    raise HTTPException(status_code=404, detail="Post not found")

@app.delete("/posts/{post_id}", status_code=204)
def delete_post(post_id: int):
    for index, post in enumerate(BLOG_POSTS):
        if post["id"] == post_id:
            BLOG_POSTS.pop(index)
            return
    raise HTTPException(status_code=404, detail="Post not found")