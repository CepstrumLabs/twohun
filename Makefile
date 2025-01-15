# Variables
PYTHON = python3
PIP = pip3
NPM = npm
BACKEND_APP = app.main:app
FRONTEND_DIR = frontend
BACKEND_DIR = backend
VENV = venv
ENV ?= dev  # Default to dev environment

# Python venv executables
VENV_PYTHON = ./$(VENV)/bin/python
VENV_PIP = ./$(VENV)/bin/pip
VENV_UVICORN = ./$(VENV)/bin/uvicorn

# Configuration based on environment
define set_config
    ifeq ($(strip $(1)),dev)
        BACKEND_CONFIG = --reload --port 8000 --host 127.0.0.1
        FRONTEND_CMD = start
        ENV_FILE = .env.development
    else
        BACKEND_CONFIG = --port 8000 --host 0.0.0.0 --workers 4
        FRONTEND_CMD = serve
        ENV_FILE = .env.production
    endif
endef

# Virtual environment setup
.PHONY: venv
venv:
	test -d $(VENV) || $(PYTHON) -m venv $(VENV)
	$(VENV_PIP) install --upgrade pip

# Install dependencies
.PHONY: install
install: venv
	$(VENV_PIP) install -r $(BACKEND_DIR)/requirements.txt
	cd $(FRONTEND_DIR) && $(NPM) install

# Development commands
.PHONY: dev
dev: db-recreate install
	$(eval $(call set_config,$(ENV)))
	@echo "Starting services in order..."
	@echo "1. Starting database..."
	docker-compose up -d db
	@echo "Waiting for database..."
	sleep 3
	
	@echo "2. Starting frontend..."
	cd $(FRONTEND_DIR) && $(NPM) $(FRONTEND_CMD) & \
	echo "Waiting for frontend..."
	sleep 5
	
	@echo "3. Starting backend API..."
	cd $(BACKEND_DIR) && ENV=dev PYTHONPATH=$(BACKEND_DIR) ../$(VENV_UVICORN) $(BACKEND_APP) $(BACKEND_CONFIG) & \
	wait

# Production commands
.PHONY: prod
prod: venv
	@trap 'kill %1; kill %2' SIGINT; \
	cd $(BACKEND_DIR) && ENV=prod $(VENV_UVICORN) $(BACKEND_APP) $(BACKEND_CONFIG) & \
	cd $(FRONTEND_DIR) && ENV_FILE=$(ENV_FILE) $(NPM) run build && $(NPM) run serve & \
	wait

# Utility commands
.PHONY: clean
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name "node_modules" -exec rm -rf {} +
	find . -type d -name "build" -exec rm -rf {} +
	rm -rf $(VENV)

# Database commands
.PHONY: db-up
db-up:
	docker-compose up -d db

.PHONY: db-down
db-down:
	docker-compose down

.PHONY: db-reset
db-reset:
	@echo "Resetting database..."
	@PGPASSWORD=twohun_password psql -h localhost -U twohun -d twohun_db -c "DROP TABLE IF EXISTS stocks CASCADE;"
	@PGPASSWORD=twohun_password psql -h localhost -U twohun -d twohun_db -c "DROP SEQUENCE IF EXISTS stocks_id_seq CASCADE;"
	@echo "Database reset complete"

# Add a complete reset that recreates the database
.PHONY: db-recreate
db-recreate:
	@echo "Recreating database..."
	docker-compose down -v
	docker-compose up -d db
	@echo "Waiting for database to be ready..."
	@sleep 3
	@echo "Database recreated"

# Stack commands
.PHONY: down
down:
	echo "Stopping all services..."
	pkill -f "uvicorn" || true
	pkill -f "node" || true
	docker-compose down
	echo "All services stopped"

.PHONY: help
help:
	@echo "Available commands:"
	@echo "  make install  - Install all dependencies"
	@echo "  make dev      - Start development servers"
	@echo "  make prod     - Start production servers"
	@echo "  make clean    - Clean up generated files"
	@echo "  make db-up    - Start the database"
	@echo "  make db-down  - Stop the database"
	@echo "  make db-reset - Reset database schema"
	@echo "  make down     - Stop all services" 