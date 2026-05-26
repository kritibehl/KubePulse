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


.PHONY: capacity-demo

capacity-demo:
	python3 scripts/capacity_release_check.py


.PHONY: scaling-demo rollback-demo dependency-demo

scaling-demo:
	python3 scripts/render_scaling_comparison.py

rollback-demo:
	python3 scripts/simulate_canary_failure_rollback.py

dependency-demo:
	python3 scripts/analyze_dependency_health.py


.PHONY: deployment-wave-demo

deployment-wave-demo:
	python3 scripts/validate_deployment_wave.py


.PHONY: deployment-ui-demo

deployment-ui-demo:
	python3 scripts/render_deployment_dashboard.py
	@echo "Open UI: ui/deployment_dashboard/index.html"
	@echo "Screenshot: docs/screenshots/deployment_safety_dashboard.png"


.PHONY: security-demo

security-demo:
	python3 scripts/security_release_check.py
