.PHONY: snapshot metrics time-start time-stop validate-data validate-models test reproduce quality dashboard

PYTHON ?= python3

snapshot:
	$(PYTHON) scripts/create_snapshot.py --reason "make snapshot"

metrics:
	$(PYTHON) scripts/project_metrics.py

time-start:
	$(PYTHON) scripts/time_tracker.py start --task "$(TASK)"

time-stop:
	$(PYTHON) scripts/time_tracker.py stop

validate-data:
	$(PYTHON) scripts/validate_all_data.py

validate-models:
	$(PYTHON) scripts/validate_models.py

test:
	$(PYTHON) -m pytest tests/ -q -m "not slow"
	cd settlement_lab && PYTHONPATH=. $(PYTHON) -m pytest tests/ -q

reproduce:
	$(PYTHON) scripts/reproduce_all.py

quality:
	$(PYTHON) scripts/run_all_quality_checks.py

dashboard:
	streamlit run src/dashboard/app.py
