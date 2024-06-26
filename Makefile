
.PHONY: build
build:
	docker-compose up --build -d


.PHONY: up
up:
	docker-compose up


.PHONY: down
down:
	docker-compose down

.PHONY: down-clean

down-clean:
	docker-compose down --volumes

.PHONY: logs 
logs:
	docker-compose logs -f --tail=100

.PHONY: restart
restart:
	docker-compose restart
	docker-compose logs -f --tail=100


.PHONY: migrate
migrate:
	docker-compose exec api alembic upgrade head


.PHONY: test
test:
	pytest tests/test_auth.py
	pytest tests/test_receipts.py


.PHONY: install
install:
	pip install poetry
	poetry install