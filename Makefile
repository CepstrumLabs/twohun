# Variables
PYTHON = python3
PIP = pip3
NPM = npm
UVICORN = uvicorn
BACKEND_APP = backend.app.main:app
FRONTEND_DIR = frontend
BACKEND_DIR = backend
ENV ?= dev  # Default to dev environment

# Configuration based on environment
ifeq ($(ENV),dev)
    BACKEND_CONFIG = --reload --port 8000 --host 127.0.0.1
    FRONTEND_CMD = start
    ENV_FILE = .env.development
else
    BACKEND_CONFIG = --port 8000 --host 0.0.0.0 --workers 4
    FRONTEND_CMD = serve
    ENV_FILE = .env.production
endif

# Development commands
.PHONY: install
install:
	cd $(BACKEND_DIR) && $(PIP) install -r requirements.txt
	cd $(FRONTEND_DIR) && $(NPM) install

.PHONY: dev
dev:
	@trap 'kill %1; kill %2' SIGINT; \
	cd $(BACKEND_DIR) && ENV=dev $(UVICORN) $(BACKEND_APP) $(BACKEND_CONFIG) & \
	cd $(FRONTEND_DIR) && ENV_FILE=$(ENV_FILE) $(NPM) start & \
	wait

# Production commands
.PHONY: prod
prod:
	@trap 'kill %1; kill %2' SIGINT; \
	cd $(BACKEND_DIR) && ENV=prod $(UVICORN) $(BACKEND_APP) $(BACKEND_CONFIG) & \
	cd $(FRONTEND_DIR) && ENV_FILE=$(ENV_FILE) $(NPM) run build && $(NPM) run serve & \
	wait

# Build commands
.PHONY: build
build:
	cd $(FRONTEND_DIR) && ENV_FILE=$(ENV_FILE) $(NPM) run build

# Utility commands
.PHONY: clean
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name "node_modules" -exec rm -rf {} +
	find . -type d -name "build" -exec rm -rf {} +

.PHONY: help
help:
	@echo "Available commands:"
	@echo "  make install              - Install all dependencies"
	@echo "  make dev                  - Start development servers"
	@echo "  make prod                 - Start production servers"
	@echo "  make build ENV=prod       - Build for production"
	@echo "  make build ENV=dev        - Build for development"
	@echo "  make clean               - Clean up generated files" 