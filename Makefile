.PHONY: help build up down restart logs clean test dev setup migrate

# Colors
BLUE=\033[0;34m
GREEN=\033[0;32m
RED=\033[0;31m
NC=\033[0m # No Color

help: ## Show this help message
	@echo "$(BLUE)JARVIS AI Assistant - Make Commands$(NC)"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(GREEN)%-15s$(NC) %s\n", $$1, $$2}'

setup: ## Initial setup - copy .env and install dependencies
	@echo "$(BLUE)Setting up JARVIS AI Assistant...$(NC)"
	@if [ ! -f .env ]; then \
		cp .env.example .env; \
		echo "$(GREEN)✓ Created .env file$(NC)"; \
		echo "$(RED)⚠ Please edit .env with your configuration$(NC)"; \
	else \
		echo "$(GREEN)✓ .env already exists$(NC)"; \
	fi

build: ## Build Docker images
	@echo "$(BLUE)Building Docker images...$(NC)"
	docker-compose build

up: ## Start all services
	@echo "$(BLUE)Starting services...$(NC)"
	docker-compose up -d
	@echo "$(GREEN)✓ Services started!$(NC)"
	@echo ""
	@echo "Access points:"
	@echo "  Frontend:  http://localhost"
	@echo "  API Docs:  http://localhost:8000/api/docs"
	@echo "  Health:    http://localhost:8000/health"

down: ## Stop all services
	@echo "$(BLUE)Stopping services...$(NC)"
	docker-compose down
	@echo "$(GREEN)✓ Services stopped$(NC)"

restart: down up ## Restart all services

logs: ## Show logs (use SERVICE=backend to filter)
	@if [ -z "$(SERVICE)" ]; then \
		docker-compose logs -f; \
	else \
		docker-compose logs -f $(SERVICE); \
	fi

clean: ## Remove all containers, volumes, and images
	@echo "$(RED)WARNING: This will remove all data!$(NC)"
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		docker-compose down -v --rmi all; \
		echo "$(GREEN)✓ Cleaned up$(NC)"; \
	fi

migrate: ## Run database migrations
	@echo "$(BLUE)Running migrations...$(NC)"
	docker exec jarvis_backend alembic upgrade head
	@echo "$(GREEN)✓ Migrations applied$(NC)"

migrate-create: ## Create new migration (use MSG="description")
	@if [ -z "$(MSG)" ]; then \
		echo "$(RED)Error: Please provide MSG=\"description\"$(NC)"; \
		exit 1; \
	fi
	docker exec jarvis_backend alembic revision --autogenerate -m "$(MSG)"
	@echo "$(GREEN)✓ Migration created$(NC)"

test: ## Run backend tests
	@echo "$(BLUE)Running tests...$(NC)"
	docker exec jarvis_backend pytest -v

test-cov: ## Run tests with coverage
	@echo "$(BLUE)Running tests with coverage...$(NC)"
	docker exec jarvis_backend pytest -v --cov=app --cov-report=html
	@echo "$(GREEN)✓ Coverage report generated in htmlcov/$(NC)"

dev: ## Start development environment (only DB and Redis)
	@echo "$(BLUE)Starting development environment...$(NC)"
	docker-compose up -d postgres redis
	@echo "$(GREEN)✓ Database and Redis started$(NC)"
	@echo ""
	@echo "Run manually:"
	@echo "  Backend:  cd backend && uvicorn app.main:app --reload"
	@echo "  Frontend: cd frontend && npm run dev"

shell-backend: ## Open shell in backend container
	docker exec -it jarvis_backend /bin/bash

shell-db: ## Open PostgreSQL shell
	docker exec -it jarvis_postgres psql -U jarvis -d jarvis_db

shell-redis: ## Open Redis CLI
	docker exec -it jarvis_redis redis-cli

ollama-pull: ## Pull Ollama model (use MODEL=mistral)
	@if [ -z "$(MODEL)" ]; then \
		echo "$(RED)Error: Please provide MODEL=model_name$(NC)"; \
		echo "Examples: make ollama-pull MODEL=mistral"; \
		exit 1; \
	fi
	docker exec jarvis_ollama ollama pull $(MODEL)
	@echo "$(GREEN)✓ Model $(MODEL) pulled$(NC)"

ollama-list: ## List available Ollama models
	docker exec jarvis_ollama ollama list

backup-db: ## Backup database to backup.sql
	@echo "$(BLUE)Backing up database...$(NC)"
	docker exec jarvis_postgres pg_dump -U jarvis jarvis_db > backup_$(shell date +%Y%m%d_%H%M%S).sql
	@echo "$(GREEN)✓ Database backed up$(NC)"

restore-db: ## Restore database from backup.sql
	@if [ ! -f backup.sql ]; then \
		echo "$(RED)Error: backup.sql not found$(NC)"; \
		exit 1; \
	fi
	@echo "$(BLUE)Restoring database...$(NC)"
	cat backup.sql | docker exec -i jarvis_postgres psql -U jarvis jarvis_db
	@echo "$(GREEN)✓ Database restored$(NC)"

status: ## Show service status
	@echo "$(BLUE)Service Status:$(NC)"
	@docker-compose ps

install: setup build up migrate ## Complete installation (setup + build + up + migrate)
	@echo ""
	@echo "$(GREEN)🎉 JARVIS AI Assistant installed successfully!$(NC)"
	@echo ""
	@echo "Next steps:"
	@echo "  1. Visit http://localhost"
	@echo "  2. Create an account"
	@echo "  3. Start chatting!"

