import pytest



@pytest.mark.asyncio
async def test_get_pokemon(async_client):
  response = await async_client.get(f"/api/v1/pokemon/3")
  assert response.status_code == 200
  assert response.json()['id'] == 3


@pytest.mark.asyncio
async def test_get_pokemon_by_name(async_client):
  response = await async_client.get(f"/api/v1/pokemon/name/bulbasaur")
  assert response.status_code == 200
  assert response.json()['name'] == 'bulbasaur'