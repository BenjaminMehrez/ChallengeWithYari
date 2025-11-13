docker-compose -f docker-compose-test.yml up --build --force-recreate -d
sleep 5
pytest --cov=app --cov-report=term --cov-report=html
docker-compose -f docker-compose-test.yml down
open htmlcov/index.html