# FastAPI Blog

A beginner-friendly Python project that combines server-rendered HTML pages, a JSON REST API, SQLite persistence, request validation, and automated tests.

## Features

- Blog homepage at `/` and `/posts`
- Individual HTML post pages at `/posts/{post_id}`
- Browser-based post creation form at `/posts/new`
- JSON endpoints to list and retrieve posts
- `POST /api/posts` to create a post
- SQLite storage so posts remain after the server restarts
- Pydantic request validation and clear `404` responses
- Database inspection utility for checking records and data integrity
- Pytest tests for page routing, API behavior, validation, and persistence
- Interactive API documentation at `/docs`

## Requirements

- Python 3.12 or newer
- `uv`

## Setup

From the project root, install the dependencies:

```powershell
uv sync
```

## Run the Application

```powershell
uv run fastapi dev src/fastapi_blog/__init__.py
```

Open these URLs in your browser:

- Blog: http://127.0.0.1:8000
- API documentation: http://127.0.0.1:8000/docs

## API Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/` | Display the blog homepage |
| GET | `/posts` | Display blog posts |
| GET | `/posts/new` | Show the create-post form |
| POST | `/posts/new` | Create a post through the HTML form |
| GET | `/posts/{post_id}` | Display an individual post |
| GET | `/api/posts` | List all posts as JSON |
| GET | `/api/posts/{post_id}` | Retrieve one post as JSON |
| POST | `/api/posts` | Create a post through the API |

### Example API Request

Request body for `POST /api/posts`:

```json
{
  "author": "Jenisha",
  "title": "My first API post",
  "content": "This post is stored in SQLite."
}
```

## Database

The application uses SQLite to store blog posts persistently.

- The database file, `blog.db`, is created in the project root on first run.
- Two example posts are inserted if the posts table is empty.
- Set the `BLOG_DATABASE_PATH` environment variable to use a different database location.

### Inspect Database Records

Run the database inspection script from the project root:

```powershell
uv run python check_database.py
```

The script runs read-only SQL queries to inspect:

- Database tables and column structure
- All posts and total post count
- Posts filtered by ID or author
- Title and content keyword searches
- Post counts grouped by author
- Empty fields and duplicate titles
- Title lengths and post ID ranges

The script does not create, update, or delete blog posts.

## Run Tests

Run the automated test suite using Pytest:

```powershell
uv run pytest
```

The tests use a temporary SQLite database and do not modify your normal local blog database.

### Test Coverage

The test suite uses Pytest and FastAPI's `TestClient` to verify:

- HTML page rendering and navigation
- REST API responses and post retrieval
- Post creation and database persistence
- Input validation and error handling
- HTML form submission and redirects
- Handling of nonexistent posts

**Test Results:** All 12 automated tests passed in the latest test run.

## Project Structure

```text
fastapi_blog/
├── pyproject.toml
├── uv.lock
├── README.md
├── .gitignore
├── check_database.py
├── src/
│   └── fastapi_blog/
│       └── __init__.py
├── templates/
│   ├── layout.html
│   ├── home.html
│   ├── post.html
│   ├── create_post.html
│   └── error.html
└── tests/
    └── test_blog.py
```

## Technologies

- Python
- FastAPI
- Pydantic
- SQLite and SQL
- Jinja2
- HTML and CSS
- Pytest
- uv
