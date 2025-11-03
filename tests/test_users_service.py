import pytest
from typing import List
from app.core.security import get_password_hash
from app.modules.pokemon.shemas import Pokemon
from app.modules.users.models import User
from app.modules.users.schemas import UserCreate, UserUpdate


@pytest.mark.asyncio
async def test_add_pokemon_to_user(db_session, test_user, users_service):
  db_session.add(test_user)
  db_session.commit()
  db_session.refresh(test_user)

  user = await users_service.add_pokemon_to_user(test_user.id, 6)
  pokemon = user.pokemons[1]
  assert len(user.pokemons) == 2
  assert pokemon['id'] == 6
  

def test_remove_pokemon_from_user(db_session, test_user, users_service):
  db_session.add(test_user)
  db_session.commit()
  db_session.refresh(test_user)

  user = users_service.remove_pokemon_from_user(test_user.id, 4)
  assert len(user.pokemons) == 0


def test_get_user_pokemons(db_session, test_user, users_service):
  db_session.add(test_user)
  db_session.commit()
  db_session.refresh(test_user)

  pokemons = users_service.get_user_pokemons(test_user.id)
  pokemon = pokemons[0]
  assert pokemon['id'] == 4
  assert pokemon['name'] == 'pikachu'


def test_update_user_pokemons(db_session, test_user, users_service):
  db_session.add(test_user)
  db_session.commit()
  db_session.refresh(test_user)

  newPokemons = [
      Pokemon(id=1, name="Juancho"),
      Pokemon(id=2, name="Charmander")
  ]

  user = users_service.update_user_pokemons(test_user.id, newPokemons)
  pokemon = user.pokemons[0]
  assert pokemon['id'] == 1
  assert pokemon['name'] == 'Juancho'


#### USER

def test_get_all_users(db_session, test_user, users_service):
  db_session.add(test_user)
  db_session.commit()
  db_session.refresh(test_user)

  users = users_service.get_all_users()
  assert len(users) > 0


def test_get_active_users(db_session, test_user, users_service):
  db_session.add(test_user)
  db_session.commit()
  db_session.refresh(test_user)

  users = users_service.get_active_users()
  assert len(users) > 0
  assert all(user.is_active for user in users)


def test_get_user_by_id(db_session, test_user, users_service):
  db_session.add(test_user)
  db_session.commit()
  user = users_service.get_user_by_id(test_user.id)

  assert user.id == test_user.id
  assert user.email == test_user.email


def test_get_user_by_email(db_session, test_user, users_service):
  db_session.add(test_user)
  db_session.commit()
  db_session.refresh(test_user)

  user = users_service.get_user_by_email(test_user.email)
  assert user.email == test_user.email


def test_get_user_by_username(db_session, test_user, users_service):
  db_session.add(test_user)
  db_session.commit()
  db_session.refresh(test_user)

  user = users_service.get_user_username(test_user.username)
  assert user.username == test_user.username


def test_search_users(db_session, test_user, users_service):
  db_session.add(test_user)
  db_session.commit()
  db_session.refresh(test_user)

  user = users_service.search_users('Test')
  assert user[0].email == test_user.email


def test_create_user(db_session, test_user, users_service):
  db_session.add(test_user)
  db_session.commit()
  db_session.refresh(test_user)

  newUser = UserCreate(
    email='newuser@example.com',
    username="Test2",
    password='password444'
  )

  user = users_service.create_user(newUser)
  users = users_service.get_all_users()
  assert len(users) > 1
  assert user.email == 'newuser@example.com'
  assert user.is_active == True 


def test_update_user(db_session, test_user, users_service):
  db_session.add(test_user)
  db_session.commit()
  db_session.refresh(test_user)

  updateUser = UserUpdate(
    email="updateemail@example.com",
    username="test222"
  )

  user = users_service.update_user(test_user.id, updateUser)
  assert user.id == test_user.id
  assert user.email == "updateemail@example.com"
  assert user.username == "test222"


def test_delete_user(db_session, test_user, users_service):
  db_session.add(test_user)
  db_session.commit()
  db_session.refresh(test_user)

  user = users_service.delete_user(test_user.id)
  users = users_service.get_all_users()
  assert len(users) == 0


def test_deactivate_user(db_session, test_user, users_service):
  db_session.add(test_user)
  db_session.commit()
  db_session.refresh(test_user)

  user = users_service.deactivate_user(test_user.id)
  assert user.is_active == False


def test_activate_user(db_session, test_user, users_service):
  db_session.add(test_user)
  db_session.commit()
  db_session.refresh(test_user)


  user = users_service.deactivate_user(test_user.id)
  assert user.is_active == False

  user2 = users_service.activate_user(test_user.id)
  assert user2.is_active == True