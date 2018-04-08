help:
	@echo 'Makefile for managing web application                        '
	@echo '                                                             '
	@echo 'Usage:                                                       '
	@echo ' make build      build images                                '
	@echo ' make up         creates containers and starts service       '
	@echo ' make start      starts service containers                   '
	@echo ' make stop       stops service containers                    '
	@echo ' make down       stops service and removes containers        '
	@echo '                                                             '
	@echo ' make migrate    run migrations                              '
	@echo ' make test       run tests                                   '
	@echo ' make test_cov   run tests with coverage.py                  '
	@echo ' make test_fast  run tests without migrations                '
	@echo ' make lint       run flake8 linter                           '
	@echo '                                                             '
	@echo ' make attach     attach to process inside service            '
	@echo ' make logs       see container logs                          '
	@echo ' make shell      connect to app container in new bash shell  '
	@echo ' make dbshell    connect to postgres inside db container     '
	@echo '                                                             '

build:
	docker-compose build

up:
	docker-compose up -d web db

start:
	docker-compose start web db

stop:
	docker-compose stop

down:
	docker-compose down

attach: ## Attach to web container
	$(eval CONTAINER_SHA=$(shell docker-compose ps -q web))
	docker attach $(CONTAINER_SHA)

logs:
	docker logs -f app_web

flask_shell: ## Shell into Flask process
	docker-compose exec web flask konch

shell: ## Shell into web container
	docker-compose exec web bash

dbshell: ## Shell into postgres process inside db container
	docker-compose exec db psql -U postgres -d sivdev

migration: up ## Create migrations using flask migrate
	docker-compose exec web flask db migrate -m "$(m)"

migrate: up ## Run migrations using flask migrate
	docker-compose exec web flask db upgrade

migrate_back: up ## Rollback migrations using flask migrate
	docker-compose exec web flask db downgrade

test: migrate
	docker-compose exec web pytest

test_cov: migrate
	docker-compose exec web pytest --verbose --cov

test_cov_view: migrate
	docker-compose exec web pytest --cov --cov-report html && open ./htmlcov/index.html

test_fast: ## Can pass in parameters using p=''
	docker-compose exec web pytest $(p)

# Flake 8
# options: http://flake8.pycqa.org/en/latest/user/options.html
# codes: http://flake8.pycqa.org/en/latest/user/error-codes.html
max_line_length = 100
lint: up
	docker-compose exec web flake8 \
		--max-line-length $(max_line_length)
