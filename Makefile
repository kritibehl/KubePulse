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


.PHONY: canary-demo

canary-demo:
	python3 scripts/simulate_canary_rollout.py


.PHONY: aws-release-demo

aws-release-demo:
	@echo "AWS release validation demo"
	@echo "==========================="
	@test -f infra/terraform/aws_ecs/main.tf
	@test -f aws/cloudwatch/cloudwatch_dashboard_example.json
	@test -f .github/workflows/aws_release_validation.yml
	python3 scripts/final_release_decision.py
	@echo ""
	@echo "AWS artifacts validated:"
	@echo "- infra/terraform/aws_ecs/main.tf"
	@echo "- aws/cloudwatch/cloudwatch_dashboard_example.json"
	@echo "- .github/workflows/aws_release_validation.yml"
