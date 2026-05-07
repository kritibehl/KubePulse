# C# Minimal API Service Demo

Tiny ASP.NET Core Minimal API demo used as backend-service proof.

## Endpoints

- `GET /health`
- `GET /items`
- `GET /items/{id}`

## Run

```bash
dotnet run
Smoke test
curl http://localhost:5000/health
curl http://localhost:5000/items
curl http://localhost:5000/items/1
Why this exists

This demo provides small, defensible proof of C# and ASP.NET Core Minimal API familiarity.
