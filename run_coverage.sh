set -e

docker-compose -f docker-compose-test.yml up --build --force-recreate -d
sleep 5

# Active venv
if [ -d ".venv" ]; then
    source .venv/bin/activate
else
    python -m venv .venv
    source .venv/bin/activate
fi

pytest --cov=app --cov-report=term --cov-report=html
docker-compose -f docker-compose-test.yml down
open htmlcov/index.html