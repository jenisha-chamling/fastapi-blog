from fastapi.testclient import TestClient

import fastapi_blog


def make_test_client(monkeypatch, tmp_path):
    database_path = tmp_path / "test_blog.db"
    monkeypatch.setattr(fastapi_blog, "DB_PATH", database_path)
    fastapi_blog.initialize_database()
    return TestClient(fastapi_blog.app)


def test_homepage_lists_seed_posts(monkeypatch, tmp_path):
    client = make_test_client(monkeypatch, tmp_path)
    response = client.get("/")
    assert response.status_code == 200
    assert "Latest posts" in response.text
    assert "Learning FastAPI Day 1" in response.text


def test_post_title_links_to_html_detail_page(monkeypatch, tmp_path):
    client = make_test_client(monkeypatch, tmp_path)
    response = client.get("/posts")
    assert response.status_code == 200
    assert '/posts/1' in response.text
    assert 'href="/api/posts/1"' not in response.text


def test_web_post_detail(monkeypatch, tmp_path):
    client = make_test_client(monkeypatch, tmp_path)
    response = client.get("/posts/1")
    assert response.status_code == 200
    assert "Learning FastAPI Day 1" in response.text
    assert "Jenisha" in response.text


def test_unknown_web_post_returns_404(monkeypatch, tmp_path):
    client = make_test_client(monkeypatch, tmp_path)
    response = client.get("/posts/999")
    assert response.status_code == 404


def test_api_lists_posts(monkeypatch, tmp_path):
    client = make_test_client(monkeypatch, tmp_path)
    response = client.get("/api/posts")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    titles = {post["title"] for post in response.json()}
    assert {"Learning FastAPI Day 1", "Learning Python Day 1"}.issubset(titles)


def test_api_gets_one_post(monkeypatch, tmp_path):
    client = make_test_client(monkeypatch, tmp_path)
    response = client.get("/api/posts/1")
    assert response.status_code == 200
    assert response.json()["id"] == 1


def test_api_unknown_post_returns_404(monkeypatch, tmp_path):
    client = make_test_client(monkeypatch, tmp_path)
    response = client.get("/api/posts/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Post not found"


def test_api_creates_post_and_persists_it(monkeypatch, tmp_path):
    client = make_test_client(monkeypatch, tmp_path)
    response = client.post(
        "/api/posts",
        json={"author": "Jenisha", "title": "My new post", "content": "SQLite persistence works."},
    )
    assert response.status_code == 201
    created = response.json()
    assert created["title"] == "My new post"

    read_response = client.get(f"/api/posts/{created['id']}")
    assert read_response.status_code == 200
    assert read_response.json()["content"] == "SQLite persistence works."


def test_api_rejects_blank_post_fields(monkeypatch, tmp_path):
    client = make_test_client(monkeypatch, tmp_path)
    response = client.post(
        "/api/posts",
        json={"author": "Jenisha", "title": "   ", "content": "Some content"},
    )
    assert response.status_code == 422


def test_create_post_page_is_available(monkeypatch, tmp_path):
    client = make_test_client(monkeypatch, tmp_path)
    response = client.get("/posts/new")
    assert response.status_code == 200
    assert 'name="author"' in response.text
    assert 'name="title"' in response.text
    assert 'name="content"' in response.text


def test_html_form_creates_post_and_redirects(monkeypatch, tmp_path):
    client = make_test_client(monkeypatch, tmp_path)
    response = client.post(
        "/posts/new",
        data={"author": "Jenisha", "title": "Created in browser", "content": "Form submission works."},
        follow_redirects=False,
    )
    assert response.status_code == 303
    assert response.headers["location"].startswith("http://testserver/posts/")
    detail = client.get(response.headers["location"])
    assert detail.status_code == 200
    assert "Created in browser" in detail.text
    assert "Form submission works." in detail.text


def test_html_form_rejects_blank_fields(monkeypatch, tmp_path):
    client = make_test_client(monkeypatch, tmp_path)
    response = client.post(
        "/posts/new",
        data={"author": "Jenisha", "title": "   ", "content": "Some content"},
    )
    assert response.status_code == 422
    assert "cannot be blank" in response.text
