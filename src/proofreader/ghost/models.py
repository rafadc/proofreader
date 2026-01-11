from datetime import datetime
from typing import Optional, Any
from pydantic import BaseModel

class Post(BaseModel):
    id: str
    uuid: str
    title: str
    slug: str
    html: Optional[str] = None
    mobiledoc: Optional[str] = None
    lexical: Optional[str] = None
    feature_image: Optional[str] = None
    featured: bool = False
    status: str
    visibility: str
    created_at: datetime
    updated_at: datetime
    published_at: Optional[datetime] = None
    custom_excerpt: Optional[str] = None
    url: Optional[str] = None
    excerpt: Optional[str] = None
    reading_time: Optional[int] = None
    access: bool = True
    comments: bool = False
    og_image: Optional[str] = None
    og_title: Optional[str] = None
    og_description: Optional[str] = None
    twitter_image: Optional[str] = None
    twitter_title: Optional[str] = None
    twitter_description: Optional[str] = None
    meta_title: Optional[str] = None
    meta_description: Optional[str] = None
    email_subject: Optional[str] = None
    frontmatter: Optional[str] = None
    
    # We might expect other fields, so we can allow extra
    model_config = {"extra": "ignore"}

class PostsResponse(BaseModel):
    posts: list[Post]
    meta: dict[str, Any]
