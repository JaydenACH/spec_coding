# Makefile for Respond IO Alternate Interface

.PHONY: help dev build start stop restart logs clean test lint format migrate backup restore deploy

# Default target
help:
	@echo "Available commands:"
	@echo "  help       - Show this help message"
	@echo "  dev        - Start development environment"
	@echo "  build      - Build all Docker images"
	@echo "  start      - Start services"
	@echo "  stop       - Stop services"
	@echo "  restart    - Restart services"
	@echo "  logs       - Show logs for all services"
	@echo "  clean      - Clean up Docker resources"
	@echo "  test       - Run tests"
	@echo "  lint       - Run linting"
	@echo "  format     - Format code"
	@echo "  migrate    - Run database migrations"
	@echo "  backup     - Create database backup"
	@echo "  restore    - Restore database from backup"
	@echo "  deploy     - Deploy to production"

# Development environment
dev:
	@echo "Starting development environment..."
	docker-compose up --build

dev-daemon:
	@echo "Starting development environment in background..."
	docker-compose up --build -d

# Build Docker images
build:
	@echo "Building Docker images..."
	docker-compose build

build-prod:
	@echo "Building production Docker images..."
	docker-compose -f docker-compose.prod.yml build

# Start services
start:
	@echo "Starting services..."
	docker-compose up -d

start-prod:
	@echo "Starting production services..."
	docker-compose -f docker-compose.prod.yml up -d

# Stop services
stop:
	@echo "Stopping services..."
	docker-compose down

stop-prod:
	@echo "Stopping production services..."
	docker-compose -f docker-compose.prod.yml down

# Restart services
restart:
	@echo "Restarting services..."
	docker-compose restart

restart-prod:
	@echo "Restarting production services..."
	docker-compose -f docker-compose.prod.yml restart

# Show logs
logs:
	@echo "Showing logs..."
	docker-compose logs -f

logs-backend:
	@echo "Showing backend logs..."
	docker-compose logs -f backend

logs-frontend:
	@echo "Showing frontend logs..."
	docker-compose logs -f frontend

logs-prod:
	@echo "Showing production logs..."
	docker-compose -f docker-compose.prod.yml logs -f

# Clean up Docker resources
clean:
	@echo "Cleaning up Docker resources..."
	docker-compose down -v --remove-orphans
	docker system prune -f

clean-all:
	@echo "Cleaning up all Docker resources..."
	docker-compose down -v --remove-orphans
	docker system prune -af
	docker volume prune -f

# Testing
test:
	@echo "Running tests..."
	docker-compose exec backend python manage.py test

test-frontend:
	@echo "Running frontend tests..."
	docker-compose exec frontend npm test

test-e2e:
	@echo "Running end-to-end tests..."
	docker-compose exec frontend npm run test:e2e

test-coverage:
	@echo "Running tests with coverage..."
	docker-compose exec backend pytest --cov=. --cov-report=html

# Code quality
lint:
	@echo "Running linting..."
	docker-compose exec backend flake8 .
	docker-compose exec backend black --check .
	docker-compose exec backend isort --check-only .

lint-frontend:
	@echo "Running frontend linting..."
	docker-compose exec frontend npm run lint

format:
	@echo "Formatting code..."
	docker-compose exec backend black .
	docker-compose exec backend isort .

format-frontend:
	@echo "Formatting frontend code..."
	docker-compose exec frontend npm run format

# Database operations
migrate:
	@echo "Running database migrations..."
	docker-compose exec backend python manage.py migrate

makemigrations:
	@echo "Creating database migrations..."
	docker-compose exec backend python manage.py makemigrations

shell:
	@echo "Opening Django shell..."
	docker-compose exec backend python manage.py shell

dbshell:
	@echo "Opening database shell..."
	docker-compose exec backend python manage.py dbshell

# Database backup and restore
backup:
	@echo "Creating database backup..."
	docker-compose -f docker-compose.prod.yml run --rm db_backup

restore:
	@echo "Restoring database from backup..."
	@read -p "Enter backup file name: " backup_file; \
	docker-compose exec db pg_restore -U $(POSTGRES_USER) -d $(POSTGRES_DB) -v /backups/$$backup_file

# Create superuser
createsuperuser:
	@echo "Creating superuser..."
	docker-compose exec backend python manage.py createsuperuser

# Load sample data
loaddata:
	@echo "Loading sample data..."
	docker-compose exec backend python manage.py loaddata fixtures/sample_data.json

# Production deployment
deploy:
	@echo "Deploying to production..."
	@echo "Building production images..."
	docker-compose -f docker-compose.prod.yml build
	@echo "Starting production services..."
	docker-compose -f docker-compose.prod.yml up -d
	@echo "Running migrations..."
	docker-compose -f docker-compose.prod.yml exec backend python manage.py migrate
	@echo "Collecting static files..."
	docker-compose -f docker-compose.prod.yml exec backend python manage.py collectstatic --noinput
	@echo "Deployment completed!"

# Health checks
health:
	@echo "Checking service health..."
	@curl -f http://localhost:3000 && echo "Frontend: OK" || echo "Frontend: FAIL"
	@curl -f http://localhost:8000/api/health/ && echo "Backend: OK" || echo "Backend: FAIL"

health-prod:
	@echo "Checking production service health..."
	@curl -f https://$(DOMAIN) && echo "Frontend: OK" || echo "Frontend: FAIL"
	@curl -f https://$(DOMAIN)/api/health/ && echo "Backend: OK" || echo "Backend: FAIL"

# Environment setup
setup-env:
	@echo "Setting up environment files..."
	@cp .env.example .env
	@echo "Environment file created. Please edit .env with your settings."

setup-env-prod:
	@echo "Setting up production environment files..."
	@cp .env.production.example .env.production
	@echo "Production environment file created. Please edit .env.production with your settings."

# SSL certificate setup (for production)
ssl:
	@echo "Setting up SSL certificates..."
	docker-compose -f docker-compose.prod.yml exec caddy caddy reload

# View resource usage
stats:
	@echo "Docker container resource usage:"
	@docker stats --no-stream

# Database connection
db-connect:
	@echo "Connecting to database..."
	docker-compose exec db psql -U $(POSTGRES_USER) -d $(POSTGRES_DB)

# Redis connection
redis-connect:
	@echo "Connecting to Redis..."
	docker-compose exec redis redis-cli

# Update dependencies
update-deps:
	@echo "Updating backend dependencies..."
	docker-compose exec backend pip list --outdated
	@echo "Updating frontend dependencies..."
	docker-compose exec frontend npm outdated

# Generate API documentation
docs:
	@echo "Generating API documentation..."
	docker-compose exec backend python manage.py spectacular --file schema.yml

# Installation and initial setup
install: setup-env build migrate createsuperuser
	@echo "Installation completed!"
	@echo "You can now start the development server with: make dev"

install-prod: setup-env-prod build-prod deploy
	@echo "Production installation completed!"
	@echo "Your application is now running at: https://$(DOMAIN)" 