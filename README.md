# Open Research Repository

A portfolio-quality platform for researchers to create, publish, archive, search, and manage research records such as papers, datasets, software, and presentations.

## Status
Foundation / Work in Progress

## Planned technology stack
- Python
- Flask
- React
- JavaScript
- PostgreSQL
- OpenSearch
- OpenSearch Dashboards
- Docker
- Git
- Testing
- Documentation
- Data migration

## Architecture overview
- Backend: Flask application exposing API endpoints and business logic.
- PostgreSQL: primary data store for durable research record persistence.
- OpenSearch: search engine that will index documents from PostgreSQL for fast text search and analytics.
- Dashboards: OpenSearch Dashboards provides a UI for exploring and visualizing indexed data.

PostgreSQL remains the authoritative source of truth for application data, while OpenSearch is designed to index and query that data quickly for search and discovery.

## Project goals
- Provide a clean, extensible architecture for research record management.
- Support publication, archiving, and discovery workflows.
- Keep the platform easy to maintain and evolve.
- Demonstrate full-stack development with modern tooling.

## Initial folder structure
- `frontend/`
- `backend/`
- `database/`
- `search/`
- `scripts/`
- `data/`
- `docs/`
- `.github/workflows/`
- `docker-compose.yml`
- `.env.example`
- `.gitignore`
- `README.md`
- `CONTRIBUTING.md`

## Short roadmap
1. Sprint 1: scaffold frontend, backend, database, and search services.
2. Sprint 2: add core research record models, API, and UI.
3. Sprint 3: implement search, archiving, and publishing workflows.

## Author
Fernando Ferreira

## GitHub
https://github.com/fernandoferreira20
