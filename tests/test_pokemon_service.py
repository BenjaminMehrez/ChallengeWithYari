import pytest


@pytest.mark.asyncio
async def test_get_pokemon(pokemon_service):
  pokemon = await pokemon_service.get_pokemon(5)
  assert pokemon['id'] == 5
  assert pokemon['name'] == "charmeleon"



@pytest.mark.asyncio
async def test_get_by_name(pokemon_service):
  pokemon = await pokemon_service.get_pokemon_by_name('charmeleon')
  assert pokemon['name'] == 'charmeleon'