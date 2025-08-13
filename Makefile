# MyChordHub Makefile
# 簡化Docker和開發操作的命令集

.PHONY: help build up down logs clean test lint format

# 預設目標
.DEFAULT_GOAL := help

# 顏色定義
RED=\033[0;31m
GREEN=\033[0;32m
YELLOW=\033[1;33m
BLUE=\033[0;34m
NC=\033[0m # No Color

help: ## 顯示此幫助訊息
	@echo "$(BLUE)MyChordHub 開發工具$(NC)"
	@echo "可用命令："
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "$(GREEN)%-20s$(NC) %s\n", $$1, $$2}'

# 開發環境命令
dev-build: ## 建置開發環境
	@echo "$(YELLOW)建置開發環境...$(NC)"
	docker-compose -f docker-compose.dev.yml build

dev-up: ## 啟動開發環境
	@echo "$(GREEN)啟動開發環境...$(NC)"
	docker-compose -f docker-compose.dev.yml up -d
	@echo "$(GREEN)開發環境已啟動！$(NC)"
	@echo "前端: http://localhost:3000"
	@echo "後端: http://localhost:8000"
	@echo "pgAdmin: http://localhost:5050"

dev-down: ## 停止開發環境
	@echo "$(YELLOW)停止開發環境...$(NC)"
	docker-compose -f docker-compose.dev.yml down

dev-logs: ## 顯示開發環境日誌
	docker-compose -f docker-compose.dev.yml logs -f

dev-restart: ## 重啟開發環境
	@make dev-down
	@make dev-up

# 生產環境命令
prod-build: ## 建置生產環境
	@echo "$(YELLOW)建置生產環境...$(NC)"
	docker-compose -f docker-compose.prod.yml build

prod-up: ## 啟動生產環境
	@echo "$(GREEN)啟動生產環境...$(NC)"
	docker-compose -f docker-compose.prod.yml up -d

prod-down: ## 停止生產環境
	@echo "$(YELLOW)停止生產環境...$(NC)"
	docker-compose -f docker-compose.prod.yml down

# 資料庫命令
db-reset: ## 重置資料庫
	@echo "$(RED)重置資料庫...$(NC)"
	docker-compose -f docker-compose.dev.yml exec db psql -U postgres -d mychordhub -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"
	docker-compose -f docker-compose.dev.yml exec db psql -U postgres -d mychordhub -f /docker-entrypoint-initdb.d/init.sql

db-backup: ## 備份資料庫
	@echo "$(YELLOW)備份資料庫...$(NC)"
	docker-compose -f docker-compose.dev.yml exec db pg_dump -U postgres mychordhub > backup_$(shell date +%Y%m%d_%H%M%S).sql

db-shell: ## 進入資料庫命令列
	docker-compose -f docker-compose.dev.yml exec db psql -U postgres -d mychordhub

# 應用命令
backend-shell: ## 進入後端容器
	docker-compose -f docker-compose.dev.yml exec backend bash

frontend-shell: ## 進入前端容器
	docker-compose -f docker-compose.dev.yml exec frontend sh

# 測試命令
test: ## 執行所有測試
	@echo "$(YELLOW)執行測試...$(NC)"
	docker-compose -f docker-compose.dev.yml exec backend poetry run pytest
	docker-compose -f docker-compose.dev.yml exec frontend npm test

test-backend: ## 執行後端測試
	docker-compose -f docker-compose.dev.yml exec backend poetry run pytest

test-frontend: ## 執行前端測試
	docker-compose -f docker-compose.dev.yml exec frontend npm test

# 代碼品質命令
lint: ## 執行代碼檢查
	@echo "$(YELLOW)執行代碼檢查...$(NC)"
	docker-compose -f docker-compose.dev.yml exec backend poetry run black --check .
	docker-compose -f docker-compose.dev.yml exec backend poetry run flake8
	docker-compose -f docker-compose.dev.yml exec frontend npm run lint

format: ## 格式化代碼
	@echo "$(YELLOW)格式化代碼...$(NC)"
	docker-compose -f docker-compose.dev.yml exec backend poetry run black .
	docker-compose -f docker-compose.dev.yml exec frontend npm run format

# 清理命令
clean: ## 清理Docker資源
	@echo "$(RED)清理Docker資源...$(NC)"
	docker-compose -f docker-compose.dev.yml down -v
	docker system prune -f
	docker volume prune -f

clean-all: ## 深度清理所有Docker資源
	@echo "$(RED)深度清理Docker資源...$(NC)"
	docker-compose -f docker-compose.dev.yml down -v --remove-orphans
	docker-compose -f docker-compose.prod.yml down -v --remove-orphans
	docker system prune -a -f
	docker volume prune -f

# 監控命令
status: ## 顯示服務狀態
	@echo "$(BLUE)服務狀態：$(NC)"
	docker-compose -f docker-compose.dev.yml ps

logs-backend: ## 顯示後端日誌
	docker-compose -f docker-compose.dev.yml logs -f backend

logs-frontend: ## 顯示前端日誌
	docker-compose -f docker-compose.dev.yml logs -f frontend

logs-db: ## 顯示資料庫日誌
	docker-compose -f docker-compose.dev.yml logs -f db

# 安裝與初始化
install: ## 初始化專案
	@echo "$(GREEN)初始化 MyChordHub 專案...$(NC)"
	@if [ ! -f .env ]; then \
		cp .env.example .env; \
		echo "$(YELLOW)已建立 .env 檔案，請檢查並修改設定$(NC)"; \
	fi
	@make dev-build
	@make dev-up
	@echo "$(GREEN)專案初始化完成！$(NC)"

# 更新命令
update: ## 更新並重建容器
	@echo "$(YELLOW)更新專案...$(NC)"
	git pull
	@make dev-build
	@make dev-restart
	@echo "$(GREEN)更新完成！$(NC)"