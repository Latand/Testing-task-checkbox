
.PHONY: build
build:
	docker-compose up --build


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
