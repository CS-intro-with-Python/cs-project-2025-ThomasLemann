import pytest
from server import app, db
from werkzeug.security import generate_password_hash
from server import User

@pytest.fixture
def client():
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["WTF_CSRF_ENABLED"] = False
    app.config["SECRET_KEY"] = "absolute-cinema"

    with app.app_context():
        db.create_all()
        yield app.test_client()
        db.session.remove()
        db.drop_all()


@pytest.fixture
def test_user():
    user = User(
        email="test@example.com",
        password=generate_password_hash("password123")
    )
    db.session.add(user)
    db.session.commit()
    return user

def test_login_page_loads(client):
    response = client.get("/login")
    assert response.status_code == 200


def test_user_registration(client):
    response = client.post("/login", data={
        "email": "new@example.com",
        "password": "123456"
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b"Notebook" in response.data or b"main" in response.data


def test_login_wrong_password(client, test_user):
    response = client.post("/login", data={
        "email": "test@example.com",
        "password": "wrong"
    })

    assert b"Wrong password" in response.data


def test_logout(client, test_user):
    client.post("/login", data={
        "email": "test@example.com",
        "password": "password123"
    })

    response = client.get("/logout", follow_redirects=True)
    assert response.status_code == 200

def login(client):
    client.post("/login", data={
        "email": "test@example.com",
        "password": "password123"
    })


def test_create_note(client, test_user):
    login(client)

    response = client.post("/note", data={
        "noteHeader": "My note",
        "textNote": "Hello world",
        "imageData": "base64image",
        "tags[]": ["work", "todo"]
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b"My note" in response.data


def test_all_notes_requires_login(client):
    response = client.get("/all_notes")
    assert response.status_code == 302
    assert "/login" in response.location

def test_main_page(client):
    response = client.get("/")
    assert response.status_code == 200


def test_delete_note_without_login(client):
    response = client.post("/delete_note")
    assert response.status_code == 302