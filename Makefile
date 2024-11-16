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

#  Target create_db_snapshot
create_db_snapshot:
	@echo "Creating a clone of the database..."
	bash ./scripts/db_management.sh create_db_snapshot internal personaflow

restore_db_snapshot:
	@echo "Restoring the database from the snapshot..."
	bash ./scripts/db_management.sh restore_db_snapshot internal backup.sql

# Target: help
help:
	@echo "Available commands:"
	@echo "  make migrate  - Initialize the project (run migrations and insert default user)"
	@echo "  make help  - Show this help message"
	@echo "  make stack-dev  - Start the server with auto-reload"
	@echo "  make create_db_snapshot  - Create a snapshot of the database schema"
	@echo "  make restore_db_snapshot  - Restore the database from the snapshot"

.PHONY: migrate help stack-dev
