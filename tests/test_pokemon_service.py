import pytest


@pytest.mark.asyncio
async def test_get_pokemon(async_client, mock_pokeapi):
  response = await async_client.get("/api/v1/pokemon/25")
  assert response.status_code == 200
  pokemon = response.json()
  assert pokemon['id'] == 25
  assert pokemon['name'] == "pikachu"


@pytest.mark.asyncio
async def test_get_by_name(async_client, mock_pokeapi):
  response = await async_client.get(f"/api/v1/pokemon/name/bulbasaur")
  assert response.status_code == 200
  pokemon = response.json()
  assert pokemon['id'] == 1
  assert pokemon['name'] == "bulbasaur"