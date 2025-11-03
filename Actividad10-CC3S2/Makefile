# Variables de entorno

# Actividad por defecto (se puede sobreescribir: make test ACTIVITY=coverage_pruebas)
ACTIVITY ?= mocking_objetos

# Lista de actividades disponibles
ACTIVITIES = mocking_objetos

# Flags comunes para pytest (puedes ampliarlas)
PYTEST_FLAGS ?= -q
PY_WARNINGS  ?= ignore::DeprecationWarning

# Lint (modo "relajado" por defecto para desarrollo)
LINT_MAX_LINE ?= 88
LINT_IGNORE   ?= E501,W391,W293
# Ignora F401 en reexport del __init__ y E402 solo en archivos de tests
LINT_PER_FILE ?= Actividades/mocking_objetos/models/__init__.py:F401,Actividades/*/tests/*.py:E402

# Ayuda

.PHONY: help
help:
	@echo "Uso: make [comando] [opciones]"
	@echo
	@echo "Comandos disponibles:"
	@echo "  install              Instala dependencias (requirements.txt y opcionalmente requirements-dev.txt)"
	@echo "  lint                 Formatea (ruff), ordena imports (ruff I), autofix y pasa flake8 relajado"
	@echo "  test                 Ejecuta pytest en la actividad indicada (ACTIVITY)"
	@echo "  test_all             Ejecuta pytest en todas las actividades"
	@echo "  coverage             Ejecuta pytest con cobertura unificada (todas las actividades)"
	@echo "  coverage_individual  Ejecuta la cobertura para cada actividad por separado"
	@echo "  coverage_activity    Ejecuta cobertura con gate para la actividad específica (usa setup.cfg)"
	@echo "  gates                Ejecuta lint + cobertura con gate (DevSecOps)"
	@echo "  gates_activity       Ejecuta gates para una actividad específica"
	@echo "  clean                Elimina archivos temporales, caches, etc."
	@echo
	@echo "Opciones:"
	@echo "  ACTIVITY=<nombre>    Actividad especifica (por defecto: mocking_objetos)"
	@echo "  PYTEST_FLAGS='-q -k expr'  Banderas extra para pytest"
	@echo
	@echo "Ejemplos:"
	@echo "  make install"
	@echo "  make lint"
	@echo "  make test"
	@echo "  make test ACTIVITY=mocking_objetos"
	@echo "  make coverage_activity ACTIVITY=mocking_objetos"
	@echo "  make gates_activity ACTIVITY=mocking_objetos"
	@echo "  make coverage"
	@echo "  make coverage_individual"
	@echo
	@echo "Actividades disponibles:"
	@echo "  $(ACTIVITIES)"

# Instalar dependencias

.PHONY: install
install:
	@echo "Instalando dependencias..."
	pip install -r requirements.txt
	@if [ -f requirements-dev.txt ]; then \
		echo "Instalando dependencias de desarrollo..."; \
		pip install -r requirements-dev.txt; \
	fi

# Lint / Formato (una sola diana)

.PHONY: lint
lint:
	@echo "==> Formateando con Ruff..."
	ruff format . --exclude '(^|/)(bin|lib|lib64|include|share)(/|$$)|pyvenv\.cfg'
	@echo "==> Ordenando imports (Ruff rule I)..."
	ruff check . --select I --fix --exclude '(^|/)(bin|lib|lib64|include|share)(/|$$)|pyvenv\.cfg'
	@echo "==> Autofix de reglas con Ruff (whitespace, etc.)..."
	ruff check . --fix --exclude '(^|/)(bin|lib|lib64|include|share)(/|$$)|pyvenv\.cfg'
	@echo "==> Lint con flake8 (relajado: ignora $(LINT_IGNORE); ancho $(LINT_MAX_LINE))..."
	flake8 . \
	    --exclude=venv,__pycache__,.pytest_cache,bin,lib,lib64,include,share \
	    --max-line-length=$(LINT_MAX_LINE) \
	    --extend-ignore=$(LINT_IGNORE) \
	    --per-file-ignores="$(LINT_PER_FILE)"
	@echo "Lint OK"

# Test

.PHONY: test test_all
test:
	@echo "Ejecutando pruebas en la actividad: $(ACTIVITY)"
	cd Actividades/$(ACTIVITY) && PYTHONWARNINGS="$(PY_WARNINGS)" pytest . $(PYTEST_FLAGS)

test_all:
	@echo "Ejecutando pruebas en TODAS las actividades..."
	@set -e; \
	for activity in $(ACTIVITIES); do \
	   echo "EJECUTANDO PRUEBAS EN $$activity"; \
	   ( cd Actividades/$$activity && PYTHONWARNINGS="$(PY_WARNINGS)" pytest . $(PYTEST_FLAGS) ); \
	done

# Coverage

.PHONY: coverage coverage_individual
coverage:
	@echo "Ejecutando cobertura UNIFICADA en todas las actividades..."
	@coverage erase
	@set -e; \
	for activity in $(ACTIVITIES); do \
	   echo "COVERAGE RUN en $$activity"; \
	   ( cd Actividades/$$activity && PYTHONWARNINGS="$(PY_WARNINGS)" coverage run --source=. -m pytest . $(PYTEST_FLAGS) ); \
	done
	@echo "COVERAGE COMBINADO"
	@coverage combine $$(for a in $(ACTIVITIES); do echo Actividades/$$a/.coverage; done) || true
	@coverage report -m
	@coverage html -d htmlcov

coverage_individual:
	@echo "Ejecutando cobertura individual para cada actividad..."
	@set -e; \
	for activity in $(ACTIVITIES); do \
	   echo "Generando cobertura para $$activity"; \
	   ( cd Actividades/$$activity && \
	     coverage erase && \
	     PYTHONWARNINGS="$(PY_WARNINGS)" coverage run --source=. -m pytest . $(PYTEST_FLAGS) && \
	     coverage report -m && \
	     coverage html -d htmlcov_$$activity ); \
	done

# Coverage con Gate DevSecOps (específico para una actividad)

.PHONY: coverage_activity
coverage_activity:
	@echo "==> Ejecutando cobertura con GATE (≥85%) para: $(ACTIVITY)"
	@cd Actividades/$(ACTIVITY) && \
	PYTHONWARNINGS="$(PY_WARNINGS)" \
	pytest --cov=models --cov=tests \
	       --cov-report=term-missing \
	       --cov-report=html \
	       --cov-fail-under=85 \
	       -v $(PYTEST_FLAGS)
	@echo "Gate de cobertura APROBADO (≥85%)"

# Gates DevSecOps (lint + cobertura con threshold)

.PHONY: gates gates_activity
gates: lint coverage
	@echo "==> Todos los gates APROBADOS"

gates_activity: lint coverage_activity
	@echo "==> Todos los gates APROBADOS para $(ACTIVITY)"

# Target para ejecutar después de pasar gates (ejemplo)

.PHONY: run
run: gates_activity
	@echo "==> Iniciando aplicación (gates pasados)..."
	@cd Actividades/$(ACTIVITY) && python -m models.imdb || echo "No hay main definido"

# Limpiar

.PHONY: clean
clean:
	@echo "Eliminando archivos de caché y reportes..."
	# caches python/pytest
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	rm -rf .pytest_cache
	# coverage
	rm -rf .coverage htmlcov htmlcov_* Actividades/**/.coverage 2>/dev/null || true
	coverage erase || true
	@echo "Limpieza completa."
