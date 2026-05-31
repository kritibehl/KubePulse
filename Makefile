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


.PHONY: visual-demo

visual-demo:
	python3 scripts/render_architecture_diagram.py
	python3 scripts/render_autoscaling_dashboard.py
	python3 scripts/render_blocked_rollout_report.py
	python3 scripts/render_deployment_dashboard.py
	@echo "Visual artifacts generated under docs/screenshots and docs/architecture"


.PHONY: aws-architecture-demo security-validation-demo

aws-architecture-demo:
	python3 aws_architecture/lambda_style_release_evaluator.py

security-validation-demo:
	python3 security_validation/deployment_policy_checks.py security_validation/sample_insecure_deployment.yaml
	python3 security_validation/deployment_policy_checks.py security_validation/sample_secure_deployment.yaml

.PHONY: aws-runtime-demo

aws-runtime-demo:
	python3 aws_runtime_demo/release_evaluator_lambda.py

.PHONY: apple-quality-demo

apple-quality-demo:
	python3 apple_quality_engineering/run_quality_matrix.py

.PHONY: soak-demo

soak-demo:
	python3 soak_testing/run_soak_analysis.py

.PHONY: error-budget-demo progressive-delivery-demo feature-flag-demo supply-chain-demo

error-budget-demo:
	python3 error_budget/release_freeze_decision.py

progressive-delivery-demo:
	python3 progressive_delivery/canary_simulator.py

feature-flag-demo:
	python3 feature_flags/kill_switch_policy.py
	python3 feature_flags/rollout_guard.py

supply-chain-demo:
	python3 supply_chain_gate/provenance_check.py

.PHONY: incident-commander-demo capacity-forecast-demo

incident-commander-demo:
	python3 incident_commander/incident_commander.py

capacity-forecast-demo:
	python3 capacity_forecasting/capacity_forecast.py

.PHONY: network-incident-demo dependency-path-demo failover-demo

network-incident-demo:
	python3 network_reliability/network_incident_diagnostics.py

dependency-path-demo:
	python3 network_reliability/dependency_path_analysis.py

failover-demo:
	python3 network_reliability/failover_simulation.py

.PHONY: hardware-demo

hardware-demo:
	python3 hardware_validation/hardware_release_gate.py
