import pytest


@pytest.mark.asyncio
async def test_login(async_client, test_user, db_session):
    db_session.add(test_user)
    db_session.commit()
    db_session.refresh(test_user)

    login_response = await async_client.post(
        "/api/v1/auth/login",
        json={
            "email": test_user.email,
            "password": "password123",
            "grant_type": "password"
        }
    )
    assert login_response.status_code == 200
    assert login_response.json()['access_token'] is not None
    assert len(login_response.json()['access_token']) > 0


@pytest.mark.asyncio
async def test_get_current_user(async_client, auth_headers):
    response = await async_client.get("/api/v1/auth/me", headers=auth_headers)
    assert response.status_code == 200