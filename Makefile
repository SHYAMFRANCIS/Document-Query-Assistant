.PHONY: help install run test lint deploy clean

help: ## Show this help message
	@echo "Document Query Assistant - Available Commands:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'
	@echo ""

install: ## Install dependencies using uv
	uv sync

install-dev: ## Install dependencies including dev tools
	uv sync --extra dev

run: ## Run the Streamlit app locally
	uv run streamlit run app.py

test: ## Run tests
	uv run pytest tests/ -v

test-cov: ## Run tests with coverage
	uv run pytest tests/ -v --cov=. --cov-report=html

lint: ## Run linter
	uv run ruff check .

lint-fix: ## Auto-fix linting errors
	uv run ruff check . --fix

type-check: ## Run type checking
	uv run mypy .

format: ## Format code
	uv run ruff format .

deploy-check: ## Check if app is ready for deployment
	@echo "🔍 Checking deployment readiness..."
	@test -f requirements.txt && echo "✅ requirements.txt exists" || (echo "❌ requirements.txt missing" && exit 1)
	@test -f app.py && echo "✅ app.py exists" || (echo "❌ app.py missing" && exit 1)
	@test -f .streamlit/config.toml && echo "✅ config.toml exists" || (echo "❌ config.toml missing" && exit 1)
	@uv run pytest tests/ -v --tb=short
	@uv run ruff check .
	@echo ""
	@echo "✅ Ready for deployment!"
	@echo "📖 See DEPLOYMENT.md for Streamlit Cloud deployment instructions"

deploy: deploy-check ## Deploy to Streamlit Cloud
	@echo ""
	@echo "🚀 Streamlit Cloud Deployment Instructions:"
	@echo "1. Push your code to GitHub: git push origin main"
	@echo "2. Go to https://share.streamlit.io/"
	@echo "3. Click 'New app' and select your repository"
	@echo "4. Add your Gemini API key in Advanced settings"
	@echo "5. Click Deploy!"
	@echo ""
	@echo "📖 Full guide: DEPLOYMENT.md"

clean: ## Clean up cache and build files
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete 2>/dev/null || true
	find . -name "app.log" -delete 2>/dev/null || true
	@echo "🧹 Cleaned up cache files"

setup-secrets: ## Setup local secrets file from template
	@if [ ! -f .streamlit/secrets.toml ]; then \
		cp .streamlit/secrets.toml.example .streamlit/secrets.toml; \
		echo "✅ Created .streamlit/secrets.toml from template"; \
		echo "⚠️  Don't forget to add your actual API key!"; \
	else \
		echo "ℹ️  .streamlit/secrets.toml already exists"; \
	fi
