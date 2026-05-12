# Grafana Release-Safety Artifacts

This folder contains Grafana-compatible dashboard assets and screenshot-style visual artifacts for KubePulse release validation.

## Screenshots

- `screenshots/p95_spike.png`
- `screenshots/release_block.png`
- `screenshots/alert_firing.png`
- `screenshots/recovery_window.png`
- `screenshots/degraded_path_requests.png`

These visuals show the core SRE story:

- p95 latency regression
- release blocked
- alert firing
- recovery window breach
- degraded-path requests

## Dashboard

- `dashboards/kubepulse_release_safety_dashboard.json`

The dashboard is designed around Prometheus-compatible KubePulse metrics.
