.PHONY: help instalar testes cobertura lint tipo demo rodar limpar

help: ## Mostra os alvos disponíveis
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-12s\033[0m %s\n", $$1, $$2}'

instalar: ## Instala dependências de desenvolvimento
	pip install -r requirements.txt

testes: ## Roda a suíte de testes (rápida, sem cobertura)
	pytest tests/ -v

cobertura: ## Roda os testes medindo cobertura de código
	pytest tests/ --cov=pecas_qualidade --cov-report=term-missing

lint: ## Verifica estilo e padrões de bug (ruff)
	ruff check pecas_qualidade tests scripts
	ruff format --check pecas_qualidade tests

tipo: ## Verificação estática de tipos (mypy)
	mypy pecas_qualidade/

qualidade: lint tipo testes ## Roda lint + tipos + testes (o "portão" completo)

demo: ## Executa a demonstração automática (12 aprovadas + 3 reprovadas)
	python3 -m pecas_qualidade.demo

rodar: ## Roda o sistema interativo (menu)
	python3 -m pecas_qualidade.main

limpar: ## Remove artefatos gerados (cache, arquivos de estado)
	rm -rf .pytest_cache .mypy_cache .ruff_cache
	find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
	rm -f pecas_qualidade/estado_producao.json pecas_qualidade/pecas.log relatorio_final.txt
