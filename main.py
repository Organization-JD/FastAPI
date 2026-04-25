from fastapi import FastAPI, Query, Body, HTTPException, Path
from typing import List, Optional, Union, Literal
from pydantic import BaseModel, Field, field_validator

app = FastAPI(title="My FastAPI Application")

BLOG_POST = [
    {"id": 1, "title": "Hello from FastAPI",
        "content": "My first post with FastAPI"},
    {"id": 2, "title": "My second post with FastAPI",
        "content": "My second post with FastAPI blah blah"},
    {"id": 3, "title": "Django vs FastAPI",
        "content": "FastAPI is faster for x reasons",
        "tags": [
            {"name": "Python"},
            {"name": "fastapi"},
            {"name": "Django"}
        ]},
    {"id": 4, "title": "Hello from FastAPI",
        "content": "My first post with FastAPI"},
    {"id": 5, "title": "My second post with FastAPI",
        "content": "My second post with FastAPI blah blah"},
    {"id": 6, "title": "Django vs FastAPI",
        "content": "FastAPI is faster for x reasons"},
    {"id": 7, "title": "Hello from FastAPI",
        "content": "My first post with FastAPI"},
    {"id": 8, "title": "My second post with FastAPI",
        "content": "My second post with FastAPI blah blah"},
    {"id": 9, "title": "Django vs FastAPI",
        "content": "FastAPI is faster for x reasons"},
    {"id": 10, "title": "Hello from FastAPI",
        "content": "My first post with FastAPI"},
    {"id": 11, "title": "My second post with FastAPI",
        "content": "My second post with FastAPI blah blah"},
    {"id": 12, "title": "Django vs FastAPI",
        "content": "FastAPI is faster for x reasons",
        "tags": [
            {"name": "Python"},
            {"name": "fastapi"},
            {"name": "Django"}
        ]},
    {"id": 13, "title": "Hello from FastAPI",
        "content": "My first post with FastAPI"},
    {"id": 14, "title": "My second post with FastAPI",
        "content": "My second post with FastAPI blah blah"},
    {"id": 15, "title": "Django vs FastAPI",
        "content": "FastAPI is faster for x reasons",
        "tags": [
            {"name": "Python"},
            {"name": "fastapi"},
            {"name": "Django"}
        ]},
]


SPAWM_WORDS = ["spam", "junk", "scam", "fake"]

@app.get("/")
def home():
    return {"message": "Hello, World!"}

class Tag(BaseModel):
    name: str = Field(..., min_length=2, max_length=30, description="Name of the tag (2-30 characters)", example="python")

class Author(BaseModel):
    name: str = Field(..., min_length=3, max_length=50, description="Name of the author (3-50 characters)", example="John Doe")
    email: str = Field(..., pattern=r'^\S+@\S+\.\S+$', description="Email address of the author", example="john.doe@example.com")
class PostBase(BaseModel):
    title: str
    content: Optional[str] = "New post content goes here."
    author: Optional[Author] = None
    tags: Optional[List[Tag]] = Field(default_factory=list)

class PostCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=100, description="Title of the blog post (3-100 characters)", example="My First Post")
    content: Optional[str] = Field(default="New post content goes here.", min_length=10, description="Content of the blog post", example="This is the content of my first post.")
    tags: List[Tag] = Field(default_factory=list)
    author: Optional[Author] = None
    @field_validator("title")
    @classmethod
    def not_allowed_title(cls, value:str) -> str:
        for word in SPAWM_WORDS:
            if word in value.lower():
                raise ValueError(f"Title cannot contain the word '{word}'")
        return value

class PostUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=3, max_length=100, description="Title of the blog post (3-100 characters)", example="Updated Post Title")
    content: Optional[str] = None
    tags: Optional[List[Tag]] = Field(default_factory=list)
    author: Optional[Author] = None

class PostPublic(PostBase):
    id: int

class PostSummary(BaseModel):
    id: int
    title: str

class PostPaginated(BaseModel):
    page: int
    per_page: int
    total: int
    total_pages: int
    has_prev: bool
    has_next: bool
    order_by: Literal["id", "title"]
    direction: Literal["asc", "desc"]
    search: Optional[str] = None
    limit: int
    offset: int
    items: List[PostPublic]

@app.get("/posts", response_model=PostPaginated, response_description="A paginated list of blog posts")
def list_posts(
    text: Optional[str] = Query(
        default=None,
        deprecated=True,
        description="Deprecated parameter, use 'query or search' instead."
    ),
    query: Optional[str] = Query(
        default=None,
        description="Search query for blog posts",
        alias="search",
        min_length=3,
        max_length=50,
        example="FastAPI"
    ), 
    per_page: int = Query(10, ge=1, le=50, description="Number of posts to return"),
    page: int = Query(1, ge=1, description="Page number"),
    order_by: Literal["id", "title"] = Query("id", description="Sort order of the posts"),
    direction: Literal["asc", "desc"] = Query("asc", description="Sort direction of the posts")
    ):
    results = BLOG_POST
    if query:
        results = [post for post in results if query.lower() in post["title"].lower()]
    total = len(results)
    offset = (page - 1) * per_page
    items=results[offset: offset + per_page]
    total_pages = (total + per_page - 1) // per_page
    has_prev = offset > 0
    has_next = offset + per_page < total
    results = sorted(results, key=lambda post: post[order_by], reverse=(direction == "desc"))
    return PostPaginated(
        page=offset // per_page + 1,
        per_page=per_page,
        total=total,
        total_pages=total_pages,
        has_prev=has_prev,
        has_next=has_next,
        order_by=order_by,
        direction=direction,
        search=query,
        limit=per_page,
        offset=offset,
        items=items
    )

@app.get("/posts/{post_id}", response_model=Union[PostPublic, PostSummary], response_description="Returns either the full post or a summary based on the 'include_content' query parameter")
def get_post(post_id: int = Path(..., ge=1, title="The ID of the post to retrieve", description="The ID of the post to retrieve", example=1), include_content: Optional[bool] = Query(default=True, description="Include content in the response")):
    for post in BLOG_POSTS:
        if post_id == post["id"]:
            if not include_content:
                return {"id": post["id"], "title": post["title"]}
            return post
    raise HTTPException(status_code=404, detail="Post not found")

@app.get("/posts/by-tags", response_model=List[PostPublic])
def filter_by_tags(
    tags: List[str] = Query(
        ...,
        min_length=2,
        description="Una o más etiquetas. Ejemplo: ?tags=python&tags=fastapi"
    )
):
    tags_lower = [tag.lower() for tag in tags]

    return [
        post for post in BLOG_POST if any(tag["name"].lower() in tags_lower for tag in post.get("tags", []))
    ]

@app.post("/posts", response_model=PostPublic, response_description="The created blog post")
def create_post(post: PostCreate):
    new_id = (BLOG_POSTS[-1]["id"]+1) if BLOG_POSTS else 1
    new_post = {"id": new_id, "title": post.title, "content": post.content, "author": post.author.model_dump() if post.author else None, "tags": [tag.model_dump() for tag in post.tags]}
    BLOG_POSTS.append(new_post)
    return new_post

@app.put("/posts/{post_id}", response_model=PostPublic, response_description="The updated blog post", response_model_exclude_none=True)
def update_post(post_id: int, data: PostUpdate):
    for post in BLOG_POSTS:
        if post["id"] == post_id:
            payload = data.model_dump(exclude_unset=True)
            if "title" in payload:
                post["title"] = payload["title"]
            if "content" in payload:
                post["content"] = payload["content"]
            if "author" in payload:
                post["author"] = payload["author"].model_dump() if payload["author"] else None
            if "tags" in payload:
                post["tags"] = [tag.model_dump() for tag in payload["tags"]]
            return post
    raise HTTPException(status_code=404, detail="Post not found")

@app.delete("/posts/{post_id}", status_code=204)
def delete_post(post_id: int):
    for index, post in enumerate(BLOG_POST):
        if post["id"] == post_id:
            BLOG_POST.pop(index)
            return
    raise HTTPException(status_code=404, detail="Post not found")