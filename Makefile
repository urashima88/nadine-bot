.PHONY: help start-app up down start stop restart logs logs-app logs-db clean psql migrate migrate-create \
        migrate-rollback migrate-status seed seed-local backup restore monitor health stats \
        test benchmark security-scan deploy scale

GREEN := \033[0;32m
YELLOW := \033[1;33m
RED := \033[0;31m
NC := \033[0m

OK := [OK]
WARN := [WARN]
ERR := [ERROR]

ENV_FILE := .env

DB_USER := $(shell grep -s ^DB_USER $(ENV_FILE) | cut -d '=' -f2 || echo postgres)
DB_NAME := $(shell grep -s ^DB_NAME $(ENV_FILE) | cut -d '=' -f2 || echo postgres)
PGADMIN_PORT := $(shell grep -s ^PGADMIN_PORT $(ENV_FILE) | cut -d '=' -f2 || echo 8080)

help:
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "$(GREEN)%-20s$(NC) %s\n", $$1, $$2}'

start-app: ## start app locally
	DB_HOST=localhost python -m src.main
	@echo -e "$(GREEN)$(OK) App started$(NC)"
	
up: ## start all services
	@docker compose up -d
	@echo -e "$(GREEN)$(OK) Services started$(NC)"

down: ## stop and delete containers of all services
	@docker compose down
	@echo -e "$(YELLOW)$(WARN) Services stopped$(NC)"

start: ## start containers
	@docker compose start
	@echo -e "$(GREEN)$(OK) Services started$(NC)"

stop: ## stop containers
	@docker compose stop
	@echo -e "$(YELLOW)$(WARN) Services stopped$(NC)"

restart: down up ## restart all services

logs: ## show logs of all services
	@docker compose logs -f

logs-app: ## show app logs
	@docker compose logs -f bot

logs-db: ## show db logs
	@docker compose logs -f postgres

clean: ## complete cleanup
	@docker compose down -v --rmi all 2>/dev/null || true
	@docker system prune -af
	@echo -e "$(YELLOW)$(WARN) All data has been deleted$(NC)"

psql: ## connect to db via psql
	@docker compose exec postgres psql -U $(DB_USER) -d $(DB_NAME)

migrate: ## apply migrations
	@docker compose run --rm migration-runner python /app/src/database/migrate.py migrate
	@echo -e "$(GREEN)$(OK) Migrations applied$(NC)"

migrate-create: ## create new migration
	@if [ -z "$(name)" ]; then \
		echo -e "$(RED)Specify the migration name: make migrate-create name=\"description\"$(NC)"; \
		exit 1; \
	fi
	@docker compose run --rm migration-runner python /app/src/database/migrate.py create "$(name)"

migrate-rollback: ## rollback migration
	@docker compose run --rm migration-runner python /app/src/database/migrate.py rollback $(if $(steps),$(steps),1)

migrate-status: ## check migration status
	@docker compose run --rm migration-runner python /app/src/database/migrate.py status

seed: ## load test data
	@docker compose run --rm bot python -m app.database.seed
	@echo -e "$(GREEN)$(OK) Test data loaded$(NC)"

seed-local: ## load test data locally
	DB_HOST=localhost python -m src.database.seed
	@echo -e "$(GREEN)$(OK) Test data loaded$(NC)"

backup: ## create db backup
	@docker compose exec postgres pg_dump -U $(DB_USER) -Fc $(DB_NAME) \
		> backup_$(shell date +%Y%m%d_%H%M%S).dump
	@echo -e "$(GREEN)$(OK) Backup created$(NC)"

restore: ## restore db from backup
	@if [ -z "$(file)" ]; then \
		echo -e "$(RED)Specify the file: make restore file=backup.dump$(NC)"; \
		exit 1; \
	fi
	@docker compose exec -T postgres pg_restore -U $(DB_USER) -d $(DB_NAME) \
		--clean --if-exists --single-transaction $(file)
	@echo -e "$(GREEN)$(OK) Database restored$(NC)"

monitor: ## open monitoring
	@echo -e "$(YELLOW)PGAdmin:$(NC) http://localhost:$(PGADMIN_PORT)"

health: ## check health of services
	@docker compose ps
	@echo ""
	@echo -e "\n$(YELLOW)Health checks:$(NC)"
	@docker compose exec postgres pg_isready -U $(DB_USER)

stats: ## show db stats
	@docker compose exec postgres psql -U $(DB_USER) -d $(DB_NAME) -c "\dt+"

test: ## start tests
	@docker compose run --rm bot python -m pytest tests/ -v

benchmark: ## start db benchmark
	@docker compose run --rm bot python -m app.database.benchmark

security-scan: ## check configuration and images
	@docker run --rm -v "$(PWD)":/target aquasec/trivy config /target
	@for img in $$( docker compose images -q bot postgres ); do \
		docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
			aquasec/trivy image $$img; \
	done

# prod
deploy: ## start services in prod
	@echo -e "$(YELLOW)Deploy to production...$(NC)"
	@docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d
	@echo -e "$(GREEN)$(OK) Deploy completed$(NC)"

scale: ## scale bot service
	@docker compose up -d --scale bot=$(if $(N),$(N),3) --no-recreate
	@echo -e "$(GREEN)$(OK) The application has been scaled$(NC)"