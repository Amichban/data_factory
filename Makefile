.PHONY: help dev stop clean test deploy

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

dev: ## Start local development
	docker-compose up -d
	cd apps/api && uvicorn main:app --reload --host 0.0.0.0 --port 8000 &
	cd apps/web && npm run dev &
	@echo "✅ API: http://localhost:8000"
	@echo "✅ Web: http://localhost:3000"

stop: ## Stop all services
	docker-compose stop
	pkill -f "uvicorn main:app" || true
	pkill -f "next dev" || true

clean: ## Clean everything
	docker-compose down -v
	rm -rf apps/web/.next apps/web/node_modules
	rm -rf apps/api/__pycache__

test: ## Run tests
	cd apps/api && python -m pytest
	cd apps/web && npm test

deploy: ## Deploy to GCP Cloud Run
	gcloud builds submit --config cloudbuild.yaml

setup: ## Initial setup
	cp .env.example .env
	cd apps/api && pip install -r requirements.txt
	cd apps/web && npm install
	@echo "✅ Setup complete! Run 'make dev' to start"