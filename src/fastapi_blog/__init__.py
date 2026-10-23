"""FastAPI blog application with HTML pages and a JSON API."""

import os
import sqlite3
from contextlib import closing
from pathlib import Path
from typing import Annotated

from fastapi import FastAPI, Form, HTTPException, Path as ApiPath, status
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field, ValidationError
from starlette.requests import Request
from starlette.responses import RedirectResponse

app = FastAPI(title="FastAPI Blog", description="A simple blog with HTML pages and a JSON API.", version="0.2.0")

PROJECT_ROOT = Path(__file__).resolve().parents[2]
TEMPLATES_DIR = PROJECT_ROOT / "templates"
DEFAULT_DB_PATH = PROJECT_ROOT / "blog.db"
DB_PATH = Path(os.environ.get("BLOG_DATABASE_PATH", str(DEFAULT_DB_PATH)))
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


class PostCreate(BaseModel):
    """Fields required to create a blog post."""

    author: str = Field(min_length=1, max_length=80)
    title: str = Field(min_length=1, max_length=160)
    content: str = Field(min_length=1, max_length=10_000)

    # Normalize surrounding whitespace and reject values that are blank after trimming.
    def model_post_init(self, __context: object) -> None:
        for field_name in ("author", "title", "content"):
            value = getattr(self, field_name).strip()
            if not value:
                raise ValueError(f"{field_name.capitalize()} cannot be blank.")
            object.__setattr__(self, field_name, value)


class Post(PostCreate):
    id: int
    date_posted: str


def get_connection() -> sqlite3.Connection:
    """Open a SQLite connection and return rows as dictionaries."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database() -> None:
    """Create the posts table and insert starter posts only when the table is empty."""
    with closing(get_connection()) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS posts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                author TEXT NOT NULL CHECK(length(trim(author)) > 0),
                title TEXT NOT NULL CHECK(length(trim(title)) > 0),
                content TEXT NOT NULL CHECK(length(trim(content)) > 0),
                date_posted TEXT NOT NULL
            )
            """
        )
        count = connection.execute("SELECT COUNT(*) FROM posts").fetchone()[0]
        if count == 0:
            connection.executemany(
                "INSERT INTO posts (author, title, content, date_posted) VALUES (?, ?, ?, ?)",
                [
                    ("Jenisha", "Learning FastAPI Day 1", "FastAPI helps us build web applications and APIs with Python.", "Oct 11, 2026"),
                    ("Nisha", "Learning Python Day 1", "Python is a beginner-friendly programming language.", "Oct 12, 2026"),
                ],
            )
        connection.commit()


def row_to_post(row: sqlite3.Row) -> dict:
    return {key: row[key] for key in ("id", "author", "title", "content", "date_posted")}


def find_post(post_id: int) -> dict:
    with closing(get_connection()) as connection:
        row = connection.execute(
            "SELECT id, author, title, content, date_posted FROM posts WHERE id = ?",
            (post_id,),
        ).fetchone()
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    return row_to_post(row)


initialize_database()


@app.get("/", include_in_schema=False, name="home")
@app.get("/posts", include_in_schema=False, name="posts_page")
def home(request: Request):
    with closing(get_connection()) as connection:
        rows = connection.execute(
            "SELECT id, author, title, content, date_posted FROM posts ORDER BY id DESC"
        ).fetchall()
    return templates.TemplateResponse(
        request,
        "home.html",
        {"posts": [row_to_post(row) for row in rows], "title": "Home"},
    )


@app.get("/posts/new", include_in_schema=False, name="new_post_page")
def new_post_page(request: Request):
    return templates.TemplateResponse(
        request,
        "create_post.html",
        {"title": "Create a post", "errors": {}, "form_data": {}},
    )


@app.post("/posts/new", include_in_schema=False, name="create_webpost")
def create_webpost(
    request: Request,
    author: Annotated[str, Form()],
    title: Annotated[str, Form()],
    content: Annotated[str, Form()],
):
    form_data = {"author": author, "title": title, "content": content}
    try:
        post_data = PostCreate(**form_data)
    except ValidationError as exc:
        errors = {}
        for error in exc.errors():
            location = error.get("loc", ())
            field_name = str(location[0]) if location else "form"
            errors[field_name] = error["msg"]
        return templates.TemplateResponse(
            request,
            "create_post.html",
            {
                "title": "Create a post",
                "errors": errors,
                "form_data": form_data,
            },
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )

    created_post = create_post(post_data)
    return RedirectResponse(
        url=str(request.url_for("get_webpost", post_id=created_post["id"])),
        status_code=status.HTTP_303_SEE_OTHER,
    )


@app.get("/posts/{post_id}", include_in_schema=False, name="get_webpost")
def get_webpost(
    request: Request,
    post_id: Annotated[int, ApiPath(gt=0)],
):
    post = find_post(post_id)
    return templates.TemplateResponse(
        request,
        "post.html",
        {"post": post, "title": post["title"][:50]},
    )


@app.get("/api/posts", response_model=list[Post], tags=["posts"])
def get_posts():
    with closing(get_connection()) as connection:
        rows = connection.execute(
            "SELECT id, author, title, content, date_posted FROM posts ORDER BY id DESC"
        ).fetchall()
    return [row_to_post(row) for row in rows]


@app.get("/api/posts/{post_id}", response_model=Post, tags=["posts"])
def get_post(post_id: Annotated[int, ApiPath(gt=0)]):
    return find_post(post_id)


@app.post("/api/posts", response_model=Post, status_code=status.HTTP_201_CREATED, tags=["posts"])
def create_post(post_data: PostCreate):
    from datetime import date

    date_posted = date.today().strftime("%b %d, %Y")
    with closing(get_connection()) as connection:
        cursor = connection.execute(
            "INSERT INTO posts (author, title, content, date_posted) VALUES (?, ?, ?, ?)",
            (post_data.author, post_data.title, post_data.content, date_posted),
        )
        connection.commit()
        post_id = cursor.lastrowid
    return find_post(post_id)
