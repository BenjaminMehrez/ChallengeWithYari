"""seed default users

Revision ID: a1b2c3d4e5f6
Revises: 6744f6cde0d2
Create Date: 2025-11-13 12:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
from sqlalchemy.orm import Session
from sqlalchemy import text
from pwdlib import PasswordHash
import uuid
import json

from app.core.config import get_settings

# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = '6744f6cde0d2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

pwd_context = PasswordHash.recommended()
settings = get_settings()

def upgrade() -> None:
    """Seed default users - Only Development"""

    environment = settings.ENVIRONMENT
    debug = settings.DEBUG

    if environment == "production" and not debug:
        print("Production Mod - Seeds omits for security")
        return

    print('Environment: ', {environment})

    bind = op.get_bind()
    session = Session(bind=bind)
    
    admin_id = str(uuid.uuid4())
    user_id = str(uuid.uuid4())
    
    default_users = [
        {
            'id': admin_id,
            'email': 'admin@pokemon.com',
            'username': 'admin',
            'password': 'admin123',
            'gender': 'male',
            'pokemons': [],
            'is_active': True,
            'is_superuser': True
        },
        {
            'id': user_id,
            'email': 'ash@pokemon.com',
            'username': 'ash_ketchum',
            'password': 'pikachu123',
            'gender': 'male',
            'pokemons': [
                {
                    'id': 25,
                    'name': 'pikachu',
                },
                {
                    'id': 6,
                    'name': 'charizard',
                }
            ],
            'is_active': True,
            'is_superuser': False
        }
    ]
    
    print("\n🌱 Init seed default user...")
    
    for user_data in default_users:
        # Verify if user already exist
        result = session.execute(
            text("SELECT id FROM users WHERE email = :email"),
            {"email": user_data['email']}
        ).fetchone()
        
        if not result:
            # Hash password
            hashed_pwd = pwd_context.hash(user_data['password'])
            
            # Transform pokemons to JSON
            pokemons_json = json.dumps(user_data['pokemons'])
            
            # Insert user
            session.execute(
                text("""
                    INSERT INTO users (
                        id, email, username, hashed_password, gender,
                        pokemons, is_active, is_superuser,
                        created_at, updated_at
                    )
                    VALUES (
                        :id, :email, :username, :hashed_password, :gender,
                        :pokemons, :is_active, :is_superuser,
                        NOW(), NOW()
                    )
                """),
                {
                    'id': user_data['id'],
                    'email': user_data['email'],
                    'username': user_data['username'],
                    'hashed_password': hashed_pwd,
                    'gender': user_data['gender'],
                    'pokemons': pokemons_json,
                    'is_active': user_data['is_active'],
                    'is_superuser': user_data['is_superuser']
                }
            )
            
            role = "🔑 Admin" if user_data['is_superuser'] else "👤 User"
            pokemons_count = len(user_data['pokemons'])
            print(f"  ✅ {role} created: {user_data['email']} | Pokémons: {pokemons_count}")
        else:
            print(f"  ⏭️  User already exists: {user_data['email']}")
    
    session.commit()
    print("✨ Seed compleated success\n")


def downgrade() -> None:
    """Delete user of seed - Only Development."""

    environment = settings.ENVIRONMENT

    if environment == "production":
        print("Production Mod - Downgrade seeds omits for security")
        return

    bind = op.get_bind()
    session = Session(bind=bind)
    
    print("\n🗑️  Deleting user of seed...")
    
    # Delete user created in seed
    session.execute(
        text("""
            DELETE FROM users 
            WHERE email IN (
                'admin@pokemon.com',
                'ash@pokemon.com'
            )
        """)
    )
    
    session.commit()
    print("✅ User of seed deleted\n")