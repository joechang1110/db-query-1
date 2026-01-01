.PHONY: help install install-backend install-frontend dev dev-backend dev-frontend stop clean test test-backend test-frontend migrate migrate-up migrate-down lint format

# Variables
PROJECT_DIR := w2/db_query_1
BACKEND_DIR := $(PROJECT_DIR)/backend
FRONTEND_DIR := $(PROJECT_DIR)/frontend
PID_FILE := .pids
API_URL := http://localhost:8000/api/v1

help: ## Show this help message
	@echo "Database Query Tool - Makefile Commands"
	@echo ""
	@echo "Usage: make [target]"
	@echo ""
	@echo "Targets:"
	@grep -E '^[a-zA-Z0-9_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-25s %s\n", $$1, $$2}'

# Installation
install: install-backend install-frontend ## Install all dependencies

install-backend: ## Install backend dependencies
	@echo "Installing backend dependencies..."
	@cd $(BACKEND_DIR) && uv venv
	@cd $(BACKEND_DIR) && .venv/Scripts/python.exe -m pip install --upgrade pip || true
	@cd $(BACKEND_DIR) && uv pip install -e ".[dev]"
	@echo "Backend dependencies installed"

install-frontend: ## Install frontend dependencies
	@echo "Installing frontend dependencies..."
	@cd $(FRONTEND_DIR) && npm install
	@echo "Frontend dependencies installed"

# Development servers
dev: dev-backend dev-frontend ## Start both backend and frontend servers

dev-backend: ## Start backend development server
	@echo "Starting backend server..."
	@cd $(BACKEND_DIR) && if not exist .venv (echo "Error: Virtual environment not found. Run 'make install-backend' first" && exit 1)
	@cd $(BACKEND_DIR) && .venv/Scripts/python.exe -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 > nul 2>&1 & echo $$! > ../$(PID_FILE).backend
	@sleep 2
	@echo ""
	@echo "=========================================="
	@echo "Backend server is running!"
	@echo "=========================================="
	@echo "Backend: http://localhost:8000"
	@echo "API Docs: http://localhost:8000/docs"
	@echo "API Base: $(API_URL)"
	@echo ""

dev-frontend: ## Start frontend development server
	@echo "Starting frontend server..."
	@cd $(FRONTEND_DIR) && npm run dev > nul 2>&1 & echo $$! > ../$(PID_FILE).frontend
	@sleep 2
	@echo ""
	@echo "=========================================="
	@echo "Frontend server is running!"
	@echo "=========================================="
	@echo "Frontend: http://localhost:5173"
	@echo ""

# Stop servers
stop: ## Stop all running servers
	@echo "Stopping servers..."
	@# Stop backend
	@if exist $(PROJECT_DIR)/$(PID_FILE).backend ( \
		for /f "tokens=*" %%i in ($(PROJECT_DIR)/$(PID_FILE).backend) do ( \
			taskkill /F /PID %%i >nul 2>&1 && echo Backend stopped (PID: %%i) || echo Backend process not found \
		) \
		del $(PROJECT_DIR)/$(PID_FILE).backend 2>nul \
	)
	@# Stop frontend
	@if exist $(PROJECT_DIR)/$(PID_FILE).frontend ( \
		for /f "tokens=*" %%i in ($(PROJECT_DIR)/$(PID_FILE).frontend) do ( \
			taskkill /F /PID %%i >nul 2>&1 && echo Frontend stopped (PID: %%i) || echo Frontend process not found \
		) \
		del $(PROJECT_DIR)/$(PID_FILE).frontend 2>nul \
	)
	@# Kill by port (fallback)
	@for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000 ^| findstr LISTENING') do taskkill /F /PID %%a >nul 2>&1 && echo Backend stopped by port 8000 || true
	@for /f "tokens=5" %%a in ('netstat -aon ^| findstr :5173 ^| findstr LISTENING') do taskkill /F /PID %%a >nul 2>&1 && echo Frontend stopped by port 5173 || true
	@echo "Done"

# Database migrations
migrate: migrate-up ## Run database migrations (alias for migrate-up)

migrate-up: ## Run database migrations
	@echo "Running database migrations..."
	@cd $(BACKEND_DIR) && .venv/Scripts/python.exe run_migrations.py
	@echo "Migrations completed"

migrate-down: ## Rollback last migration
	@echo "Rolling back last migration..."
	@cd $(BACKEND_DIR) && .venv/Scripts/python.exe -c "from alembic import command; from alembic.config import Config; command.downgrade(Config('alembic.ini'), '-1')"
	@echo "Rollback completed"

migrate-create: ## Create a new migration (usage: make migrate-create MESSAGE="description")
	@if "$(MESSAGE)"=="" ( \
		echo Error: MESSAGE is required. Usage: make migrate-create MESSAGE="description" && \
		exit /b 1 \
	)
	@cd $(BACKEND_DIR) && .venv/Scripts/python.exe -m alembic revision --autogenerate -m "$(MESSAGE)"
	@echo Migration created

# Testing
test: test-backend ## Run all tests

test-backend: ## Run backend tests
	@echo "Running backend tests..."
	@cd $(BACKEND_DIR) && .venv/Scripts/python.exe -m pytest tests/ -v
	@echo "Tests completed"

test-backend-cov: ## Run backend tests with coverage
	@echo "Running backend tests with coverage..."
	@cd $(BACKEND_DIR) && .venv/Scripts/python.exe -m pytest tests/ --cov=app --cov-report=html --cov-report=term
	@echo "Coverage report generated in htmlcov/index.html"

# Code quality
lint: ## Run linting checks
	@echo "Running linting checks..."
	@cd $(BACKEND_DIR) && .venv/Scripts/python.exe -m ruff check app/ tests/
	@cd $(FRONTEND_DIR) && npm run lint 2>nul || echo "Frontend linting not configured"

format: ## Format code
	@echo "Formatting code..."
	@cd $(BACKEND_DIR) && .venv/Scripts/python.exe -m black app/ tests/
	@cd $(BACKEND_DIR) && .venv/Scripts/python.exe -m ruff check --fix app/ tests/
	@cd $(FRONTEND_DIR) && npm run format 2>nul || echo "Frontend formatting not configured"

# Cleanup
clean: stop ## Clean up temporary files and caches
	@echo "Cleaning up..."
	@rmdir /s /q $(BACKEND_DIR)\.venv 2>nul || true
	@rmdir /s /q $(BACKEND_DIR)\__pycache__ 2>nul || true
	@rmdir /s /q $(BACKEND_DIR)\app\__pycache__ 2>nul || true
	@rmdir /s /q $(BACKEND_DIR)\tests\__pycache__ 2>nul || true
	@rmdir /s /q $(BACKEND_DIR)\db 2>nul || true
	@rmdir /s /q $(FRONTEND_DIR)\node_modules 2>nul || true
	@rmdir /s /q $(FRONTEND_DIR)\.vite 2>nul || true
	@del /q $(PROJECT_DIR)\$(PID_FILE).* 2>nul || true
	@echo "Cleanup completed"

# Health check
health: ## Check if servers are running
	@echo "Checking server health..."
	@curl -s http://localhost:8000/health >nul 2>&1 && echo "Backend: OK" || echo "Backend: Not running"
	@curl -s http://localhost:5173 >nul 2>&1 && echo "Frontend: OK" || echo "Frontend: Not running"

