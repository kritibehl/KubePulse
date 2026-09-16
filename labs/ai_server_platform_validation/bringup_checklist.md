# AI Serving Platform Bring-up Checklist

Use this checklist before trusting an AI serving release gate.

## 1. Host Access

- [ ] SSH access works
- [ ] Host load is reasonable
- [ ] Disk space is available
- [ ] Memory pressure is acceptable

Commands:

```bash
uptime
free -h
df -h
