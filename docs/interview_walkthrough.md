# KubePulse Interview Walkthrough

## 60 seconds
KubePulse blocks Kubernetes releases that look healthy to probes but are unsafe for users.

## 3 minutes
It checks latency, error rate, DNS/TCP/TLS/auth, SLO budget, and probe integrity.

## 10 minutes
Walk through a rollout where probes pass, downstream auth fails, retries amplify load, and the release gate blocks rollout.
