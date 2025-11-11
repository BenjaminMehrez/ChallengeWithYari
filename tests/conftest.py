# Standard library
import pytest
import pytest_asyncio
import respx
import httpx
from unittest.mock import Mock
from uuid import uuid4

# Third party
from httpx import AsyncClient, ASGITransport
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Local application
from app.core.config import get_settings
from app.core.database import Base
from app.core.security import get_password_hash
from app.modules.auth.schema import TokenData
from app.modules.auth.service import AuthService
from app.modules.pokemon.service import PokeAPIService
from app.modules.users.models import User
from app.modules.users.service import UserService
from app.rate_limiting import limiter

settings = get_settings()


MOCK_POKEMON_DATA = {
    "pikachu": {
        "id": 25,
        "name": "pikachu",
        "height": 4,
        "weight": 60,
        "base_experience": 112,
        "types": [
            {
                "slot": 1,
                "type": {
                    "name": "electric",
                    "url": "https://pokeapi.co/api/v2/type/13/"
                }
            }
        ],
        "sprites": {
            "front_default": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/25.png",
            "front_shiny": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/shiny/25.png"
        },
        "abilities": [
            {
                "ability": {
                    "name": "static",
                    "url": "https://pokeapi.co/api/v2/ability/9/"
                },
                "is_hidden": False,
                "slot": 1
            },
            {
                "ability": {
                    "name": "lightning-rod",
                    "url": "https://pokeapi.co/api/v2/ability/31/"
                },
                "is_hidden": True,
                "slot": 3
            }
        ],
        "stats": [
            {"base_stat": 35, "stat": {"name": "hp"}},
            {"base_stat": 55, "stat": {"name": "attack"}},
            {"base_stat": 40, "stat": {"name": "defense"}},
            {"base_stat": 50, "stat": {"name": "special-attack"}},
            {"base_stat": 50, "stat": {"name": "special-defense"}},
            {"base_stat": 90, "stat": {"name": "speed"}}
        ]
    },
    "charizard": {
        "id": 6,
        "name": "charizard",
        "height": 17,
        "weight": 905,
        "base_experience": 267,
        "types": [
            {
                "slot": 1,
                "type": {
                    "name": "fire",
                    "url": "https://pokeapi.co/api/v2/type/10/"
                }
            },
            {
                "slot": 2,
                "type": {
                    "name": "flying",
                    "url": "https://pokeapi.co/api/v2/type/3/"
                }
            }
        ],
        "sprites": {
            "front_default": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/6.png"
        },
        "abilities": [
            {
                "ability": {
                    "name": "blaze",
                    "url": "https://pokeapi.co/api/v2/ability/66/"
                },
                "is_hidden": False,
                "slot": 1
            }
        ],
        "stats": [
            {"base_stat": 78, "stat": {"name": "hp"}},
            {"base_stat": 84, "stat": {"name": "attack"}},
            {"base_stat": 78, "stat": {"name": "defense"}},
            {"base_stat": 109, "stat": {"name": "special-attack"}},
            {"base_stat": 85, "stat": {"name": "special-defense"}},
            {"base_stat": 100, "stat": {"name": "speed"}}
        ]
    },
    "bulbasaur": {
        "id": 1,
        "name": "bulbasaur",
        "height": 7,
        "weight": 69,
        "base_experience": 64,
        "types": [
            {
                "slot": 1,
                "type": {
                    "name": "grass",
                    "url": "https://pokeapi.co/api/v2/type/12/"
                }
            },
            {
                "slot": 2,
                "type": {
                    "name": "poison",
                    "url": "https://pokeapi.co/api/v2/type/4/"
                }
            }
        ],
        "sprites": {
            "front_default": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/1.png"
        },
        "abilities": [
            {
                "ability": {
                    "name": "overgrow",
                    "url": "https://pokeapi.co/api/v2/ability/65/"
                },
                "is_hidden": False,
                "slot": 1
            }
        ],
        "stats": [
            {"base_stat": 45, "stat": {"name": "hp"}},
            {"base_stat": 49, "stat": {"name": "attack"}},
            {"base_stat": 49, "stat": {"name": "defense"}},
            {"base_stat": 65, "stat": {"name": "special-attack"}},
            {"base_stat": 65, "stat": {"name": "special-defense"}},
            {"base_stat": 45, "stat": {"name": "speed"}}
        ]
    }
}

@pytest_asyncio.fixture(scope="function")
async def mock_pokeapi():
    """ Mock automatico de PokeAPI usando respx. """
    async with respx.mock:
        # Mock for pokemon exists
        for pokemon_name, data in MOCK_POKEMON_DATA.items():
            # Mock pokemon by Name
            respx.get(f"https://pokeapi.co/api/v2/pokemon/{pokemon_name}").mock(
                return_value=httpx.Response(200, json=data)
            )
            # Mock pokemon by ID
            respx.get(f"https://pokeapi.co/api/v2/pokemon/{data['id']}").mock(
                return_value=httpx.Response(200, json=data)
            )
        
        # Mock for pokemon not find
        respx.get(url__regex=r"https://pokeapi\.co/api/v2/pokemon/.*").mock(
            return_value=httpx.Response(404, json={"detail": "Not found"})
        )
        
        yield


engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    echo=False 
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)



@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    """Crear tablas antes de todos los tests"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """Provee una sesión de BD limpia para cada test"""
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    
    try:
        yield session
    finally:
        session.close()
        transaction.rollback()  # Rollback en lugar de drop/create
        connection.close()


@pytest.fixture(scope="function")
def client(db_session):
    """Cliente de prueba con BD sobrescrita"""
    from app.main import app
    from app.core.database import get_db
    from fastapi.testclient import TestClient
    
    # Deshabilitar rate limiting
    try:
        limiter.enabled = False
    except ImportError:
        pass

    def override_get_db():
        try:
            yield db_session
        finally:
            pass 

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()




@pytest.fixture(scope="function")
def test_user(db_session):
    # Create a user with a known password hash
    password_hash = get_password_hash("password123")
    user = User(
        id=uuid4(),
        email="usertest@example.com",
        username="userTest",
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
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    db_session.expunge(user) # Desacopla el objeto de la sesión pero mantiene los datos
    return user


@pytest.fixture(scope="function")
def test_user_admin(db_session):
    # Create a user with a known password hash
    password_hash = get_password_hash("password123")
    user =  User(
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
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    db_session.expunge(user) # Desacopla el objeto de la sesión pero mantiene los datos
    return user

@pytest.fixture(scope="function")
def test_user_deactivate(db_session):
    # Create a user with a known password hash
    password_hash = get_password_hash("password123")
    user = User(
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
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    db_session.expunge(user) # Desacopla el objeto de la sesión pero mantiene los datos
    return user


@pytest.fixture(scope="function")
def test_token_data():
    return TokenData(user_id=str(uuid4()))



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


@pytest_asyncio.fixture(scope="function")
async def auth_headers(async_client):
    # Get access_token
    response = await async_client.post(
        "/api/v1/users/register",
        json={
            "email": "testtt@example.com",
            "username": "Testtt",
            "password": "testpassword123"
        }
    )
    assert response.status_code == 201

    # Login to get access token
    response = await async_client.post(
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