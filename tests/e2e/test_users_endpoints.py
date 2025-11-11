import pytest
from fastapi.testclient import TestClient


@pytest.mark.asyncio
async def test_add_pokemon_to_user(async_client, mock_pokeapi):
    register_response = await async_client.post(
        "/api/v1/users/register",
        json={
            "email": "async_test@example.com",
            "username": "AsyncTest",
            "password": "testpassword123"
        }
    )
    assert register_response.status_code == 201

    login_response = await async_client.post(
        "/api/v1/auth/login",
        json={
            "email": "async_test@example.com",
            "password": "testpassword123",
            "grant_type": "password"
        }
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    auth_headers = {"Authorization": f"Bearer {token}"}

    # Ahora usa el token
    response = await async_client.post(
        f"/api/v1/users/{register_response.json()['id']}/pokemons/6",
        headers=auth_headers
    )

    assert response.status_code == 200


def test_delete_pokemon_from_user(client: TestClient, test_user):
    login_response = client.post(
        "/api/v1/auth/login",
        json={
            "email": test_user.email,
            "password": "password123",
            "grant_type": "password"
        }
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    auth_headers = {"Authorization": f"Bearer {token}"}

    response = client.delete(
        f"/api/v1/users/{test_user.id}/pokemons/4", headers=auth_headers)
    assert response.status_code == 200


def test_get_user_pokemons(client: TestClient, test_user):
    login_response = client.post(
        "/api/v1/auth/login",
        json={
            "email": test_user.email,
            "password": "password123",
            "grant_type": "password"
        }
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    auth_headers = {"Authorization": f"Bearer {token}"}

    response = client.get(
        f"/api/v1/users/{test_user.id}/pokemons", headers=auth_headers)
    assert response.status_code == 200


def test_update_user_pokemons(client: TestClient, test_user):
    login_response = client.post(
        "/api/v1/auth/login",
        json={
            "email": test_user.email,
            "password": "password123",
            "grant_type": "password"
        }
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    auth_headers = {"Authorization": f"Bearer {token}"}

    response = client.put(f"/api/v1/users/{test_user.id}/pokemons", headers=auth_headers,
                          json=[{"id": 6, "name": "pepito"}]
                          )
    assert response.status_code == 200


def test_get_users_search(client: TestClient, auth_headers):
    response = client.get(f"/api/v1/users/search/", headers=auth_headers, params={"q": "test"})
    assert response.status_code == 200


def test_get_users(client: TestClient, auth_headers):
    response = client.get(f"/api/v1/users/", headers=auth_headers)
    assert response.status_code == 200


def test_get_user(client: TestClient, auth_headers, test_user):
    response = client.get(
        f"/api/v1/users/{test_user.id}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()['email'] == test_user.email
    assert response.json()['id'] == str(test_user.id)


def test_update_user(client: TestClient, test_user):
    login_response = client.post(
        "/api/v1/auth/login",
        json={
            "email": test_user.email,
            "password": "password123",
            "grant_type": "password"
        }
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    auth_headers = {"Authorization": f"Bearer {token}"}

    response = client.put(f"/api/v1/users/{test_user.id}", headers=auth_headers,
                          json={"email": "udpatetest3@example.com"}
                          )
    assert response.status_code == 200
    assert response.json()['email'] == "udpatetest3@example.com"
    assert response.json()['id'] == str(test_user.id)


@pytest.mark.asyncio
async def test_deactivate_user(async_client, client: TestClient, test_user,  test_user_admin):
    login_response = await async_client.post(
        "/api/v1/auth/login",
        json={
            "email": test_user_admin.email,
            "password": "password123",
            "grant_type": "password"
        }
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    auth_headers = {"Authorization": f"Bearer {token}"}

    response = client.patch(f"/api/v1/users/{test_user.id}/deactivate", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()['is_active'] == False

@pytest.mark.asyncio
async def test_activate_user(async_client, client: TestClient, test_user_deactivate,  test_user_admin):
    login_response = await async_client.post(
        "/api/v1/auth/login",
        json={
            "email": test_user_admin.email,
            "password": "password123",
            "grant_type": "password"
        }
    )
    
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    auth_headers = {"Authorization": f"Bearer {token}"}

    response = client.patch(f"/api/v1/users/{test_user_deactivate.id}/activate", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()['is_active'] == True


@pytest.mark.asyncio
async def test_delete_user(async_client, client: TestClient, test_user, test_user_admin):
    login_response = await async_client.post(
        "/api/v1/auth/login",
        json={
            "email": test_user_admin.email,
            "password": "password123",
            "grant_type": "password"
        }
    )
    
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    auth_headers = {"Authorization": f"Bearer {token}"}

    response = client.delete(f"/api/v1/users/{test_user.id}", headers=auth_headers)
    assert response.status_code == 204