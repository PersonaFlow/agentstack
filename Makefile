# Makefile

# Define variables
PYTHON := python
ALEMBIC := alembic
SERVER_DIR := stack

# Target: migrate
migrate:
	@echo "Initializing the project..."
	$(ALEMBIC) upgrade head
	PYTHONPATH=$(SERVER_DIR) $(PYTHON) scripts/setup_default_user.py
	@echo "Initialization complete."

# Target: stack-dev
stack-dev:
	@echo "Starting the development server..."
	uvicorn stack.app.main:app --reload --port 9000

# Target: help
help:
	@echo "Available commands:"
	@echo "  make migrate  - Initialize the project (run migrations and insert default user)"
	@echo "  make help  - Show this help message"
	@echo "  make stack-dev  - Start the server with auto-reload"

.PHONY: migrate help stack-dev
