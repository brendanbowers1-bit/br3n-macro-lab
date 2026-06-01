.PHONY: snapshot metrics time-start time-stop validate-data validate-models test reproduce quality dashboard command-center dashboard-visuals

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
	cd stablecoin_lab && PYTHONPATH=. $(PYTHON) -m pytest tests/ -q

reproduce:
	$(PYTHON) scripts/reproduce_all.py

quality:
	$(PYTHON) scripts/run_all_quality_checks.py

dashboard:
	streamlit run src/dashboard/app.py

command-center:
	streamlit run src/dashboard/br3n_command_center.py

dashboard-visuals:
	$(PYTHON) scripts/make_dashboard_visuals.py

dashboard-export:
	$(PYTHON) scripts/export_dashboard_api.py

data-lake-sync:
	$(PYTHON) scripts/sync_data_lake.py

dashboard-all: data-lake-sync dashboard-export dashboard-visuals
	$(PYTHON) scripts/smoke_test_command_center.py

web-dashboard-dev:
	cd web_dashboard && npm run dev

# Stablecoin Settlement Window Lab
stablecoin-fetch:
	cd stablecoin_lab && PYTHONPATH=. $(PYTHON) scripts/fetch_stablecoin_data.py

stablecoin-smoke:
	cd stablecoin_lab && PYTHONPATH=. $(PYTHON) scripts/smoke_test_stablecoin_lab.py

stablecoin-build:
	cd stablecoin_lab && PYTHONPATH=. $(PYTHON) scripts/build_stablecoin_dataset.py

stablecoin-indices:
	cd stablecoin_lab && PYTHONPATH=. $(PYTHON) scripts/run_stablecoin_indices.py

stablecoin-models:
	cd stablecoin_lab && PYTHONPATH=. $(PYTHON) scripts/run_stablecoin_models.py

stablecoin-sensitivity:
	cd stablecoin_lab && PYTHONPATH=. $(PYTHON) scripts/run_stablecoin_sensitivity.py

stablecoin-robustness:
	cd stablecoin_lab && PYTHONPATH=. $(PYTHON) scripts/run_stablecoin_robustness.py

stablecoin-visuals:
	cd stablecoin_lab && PYTHONPATH=. $(PYTHON) scripts/make_stablecoin_visuals.py

stablecoin-validate:
	cd stablecoin_lab && PYTHONPATH=. $(PYTHON) scripts/validate_stablecoin_data.py

stablecoin-reproduce:
	cd stablecoin_lab && PYTHONPATH=. $(PYTHON) scripts/reproduce_stablecoin_lab.py

stablecoin-dashboard:
	cd stablecoin_lab && PYTHONPATH=. streamlit run src/dashboard/app.py
