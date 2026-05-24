.PHONY: release-demo netroute-demo test

release-demo:
	python3 scripts/final_release_decision.py
	python3 scripts/render_network_aware_release_report.py
	@echo ""
	@echo "Release decision report:"
	@echo "docs/reports/network_aware_release_decision.html"

netroute-demo:
	python3 netroute_lab/run_network_validation.py

test:
	pytest -q
