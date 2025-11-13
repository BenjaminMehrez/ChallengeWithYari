docker-compose -f docker-compose.yml up --build --force-recreate -d
sleep 5

# Activate venv
if [ -d ".venv" ]; then
    source .venv/bin/activate
else
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements-dev.txt
fi

# Run tests
pytest --cov=app --cov-report=term --cov-report=html
docker-compose -f docker-compose.yml down
open htmlcov/index.html