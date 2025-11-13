# Backend Challenge - FastAPI Microservice

Robust REST API built with FastAPI that manages users and their Pokémon collection, integrated with PokeAPI.

## Deployed App Running on Railway

- [SWAGGER](https://challengewithyari-production.up.railway.app/docs)

### Badges

[![CircleCI](https://dl.circleci.com/status-badge/img/gh/BenjaminMehrez/ChallengeWithYari/tree/main.svg?style=svg)](https://dl.circleci.com/status-badge/redirect/gh/BenjaminMehrez/ChallengeWithYari/tree/main)

[![Coverage Status](https://coveralls.io/repos/github/BenjaminMehrez/ChallengeWithYari/badge.svg?branch=main)](https://coveralls.io/github/BenjaminMehrez/ChallengeWithYari?branch=main)

### How to run locally coveralls

```
chmod 711 ./run_coverage.sh

./run_coverage.sh
```

## Features

### User Management

- Authentication: User registration and login
- Full CRUD: Create, read, update, and delete users
- State management: Activate/deactivate user accounts
- Search and filters: Search users and retrieve statistics
- Current user: Get authenticated user information

### Pokémon Management

- Personal collection: Each user can have their own Pokémon collection
- CRUD operations: Add, update, and remove Pokémon from collection
- PokeAPI integration: Query Pokémon information by name or ID


## Pre- Requisites

- Docker installed without SUDO Permission
- Docker compose installed without SUDO
- Available ports:
  - 8000 (API)
  - 5432 (Postgresql)


## How to run the APP

```
chmod 711 ./up_dev.sh

./up_dev.sh
```

## How to run the tests

```
chmod 711 ./up_test.sh

./up_test.sh
```

## Stack

- FastAPI: Modern, high-performance web framework
- SQLAlchemy: ORM for database management
- PostgreSQL: Relational database
- Pytest: Testing framework
- Docker & Docker Compose: Containerization and orchestration
- Python 3.x: Programming language


## Architecture Decisions

- Clean Architecture: Separation of concerns in layers (domain, application, infrastructure) to facilitate future maintenance and scalability.
- SQLAlchemy: De facto standard ORM in the Python/FastAPI ecosystem, with extensive community support and documentation.
- Docker: Ensures portability and consistency across development, testing, and production environments.
- Pytest: Most widely used testing framework in Python, implemented for both unit and integration (E2E) tests.


## Identified Areas for Improvement

## Error Handling

- Improve exception handling.
- Implement standardized error responses
- Add more robust validations
 
### Database

- Implement indexes to optimize queries

## 📝 Notes

- All CRUD operations are available for both main entities
- Authentication is required for most endpoints
- Pokémon data is retrieved in real-time from PokeAPI

## Route

- Local: [API-Swagger](http://localhost:8000/docs)

## Env vars should be defined

To find an example of the values you can use .env.example
