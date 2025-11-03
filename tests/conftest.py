from httpx import AsyncClient, ASGITransport
import pytest
import pytest_asyncio
from uuid import uuid4
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.database import Base
from app.modules.auth.service import AuthService
from app.modules.pokemon.service import PokeAPIService
from app.modules.users.models import User
from app.modules.auth.schema import TokenData
from app.core.security import get_password_hash
from app.modules.users.service import UserService
from app.rate_limiting import limiter


@pytest.fixture(scope="function")
def db_session():
    # Use a unique database URL for testing
    DATABASE_TEST_URL = "sqlite:///./test.db"
    engine = create_engine(
        DATABASE_TEST_URL,
        connect_args={"check_same_thread": False}
    )
    TestingSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine
    )

    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def test_user():
    # Create a user with a known password hash
    password_hash = get_password_hash("password123")
    return User(
        id=uuid4(),
        email="test@example.com",
        username="Test",
        hashed_password=password_hash,
        pokemons=[
            {
              "id": 4,
              "name": "pikachu"
            }
        ],
        is_active=True,
        is_superuser=False
    )


@pytest.fixture(scope="function")
def test_user_admin():
    # Create a user with a known password hash
    password_hash = get_password_hash("password123")
    return User(
        id=uuid4(),
        email="testadmin@example.com",
        username="admin",
        hashed_password=password_hash,
        pokemons=[
            {
              "id": 4,
              "name": "pikachu"
            }
        ],
        is_active=True,
        is_superuser=True
    )

@pytest.fixture(scope="function")
def test_user_deactivate():
    # Create a user with a known password hash
    password_hash = get_password_hash("password123")
    return User(
        id=uuid4(),
        email="testdeactivate@example.com",
        username="testdeactivate",
        hashed_password=password_hash,
        pokemons=[
            {
              "id": 4,
              "name": "pikachu"
            }
        ],
        is_active=False,
        is_superuser=False
    )


@pytest.fixture(scope="function")
def test_token_data():
    return TokenData(user_id=str(uuid4()))


@pytest.fixture(scope="function")
def client(db_session):
    from app.main import app
    from app.core.database import get_db

    # Disable rate limiting for test
    limiter.reset()

    def override_get_db():
        try:
            yield db_session
        finally:
            db_session.close()

    app.dependency_overrides[get_db] = override_get_db

    from fastapi.testclient import TestClient
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def auth_headers(client):
    # Register a test user
    response = client.post(
        "/api/v1/users/register",
        json={
            "email": "testtt@example.com",
            "username": "Testtt",
            "password": "testpassword123"
        }
    )
    assert response.status_code == 201

    # Login to get access token
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "testtt@example.com",
            "password": "testpassword123",
            "grant_type": "password"
        }
    )
    assert response.status_code == 200
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(scope="function")
def auth_service(db_session):
    return AuthService(db=db_session)


@pytest.fixture(scope="function")
def users_service(db_session):
    return UserService(db=db_session)


@pytest.fixture(scope="function")
def pokemon_service():
    return PokeAPIService()


@pytest_asyncio.fixture(scope="function")
async def async_client(db_session):
    from app.main import app
    from app.core.database import get_db

    limiter.reset()

    def override_get_db():
        try:
            yield db_session
        finally:
            db_session.close()

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest.fixture(scope='function')
async def async_auth_headers(async_client):
    response = await async_client.post(
        "/api/v1/users/register",
        json={
            "email": "testtt@example.com",
            "username": "Testtt",
            "password": "testpassword123"
        }
    )

    assert response.status_code == 201

    response = await async_client.post(
        "/api/v1/auth/login",
        json={
            "email": "testtt@example.com",
            "password": "testpassword123",
            "grant_type": "password"
        }
    )
    assert response.status_code == 200
    token = response.json()['access_token']
    return {"Authorization": f"Bearer {token}"}
