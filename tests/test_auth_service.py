from uuid import uuid4, UUID
from app.modules.users.models import User
from app.core.security import get_password_hash, verify_password, verify_token

class TestAuthService: 
  def test_verify_password(self):
    password = "password123"
    hashed = get_password_hash(password)
    assert verify_password(password, hashed)
    assert not verify_password("wrongpassword", hashed)

  def test_authenticate_user(self, db_session, test_user, auth_service):
    db_session.add(test_user)
    db_session.commit()
    db_session.refresh(test_user)

    user = auth_service.authenticate_user("usertest@example.com", "password123")
    assert user is not False or None
    assert user.email == test_user.email

  def test_login_for_access_token(self, db_session, test_user, auth_service):
    db_session.add(test_user)
    db_session.commit()
    db_session.refresh(test_user)
    
    access_token = auth_service.create_access_token_for_user(test_user)
    
    assert access_token is not None
    assert isinstance(access_token, str)
    assert len(access_token) > 0
    
    # Opcional: Verifica que el token sea válido JWT
    parts = access_token.split('.')
    assert len(parts) == 3 


def test_create_and_verify_token(db_session, test_user, auth_service):
    db_session.add(test_user)
    db_session.commit()
    db_session.refresh(test_user)

    request = User(
        id=uuid4()
    )
    token = auth_service.create_access_token_for_user(request)

    token_data = verify_token(token)
    assert UUID(token_data['sub']) == request.id
    assert auth_service.authenticate_user("usertest@example.com", "wrong123") is None