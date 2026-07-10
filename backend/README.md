# Backend Docker Development

This backend service runs the Flask API and is prepared for future PostgreSQL connectivity.

## Build containers

Run this from the repository root:

```bash
docker compose build
```

## Start containers

Run:

```bash
docker compose up -d
```

This starts both the backend and the PostgreSQL database.

## Stop containers

Run:

```bash
docker compose stop
```
```

## Remove containers

Run:

```bash
docker compose down
```
```

## Project architecture

- `backend/` contains the Flask application and Dockerfile.
- `docker-compose.yml` defines service orchestration for local development.
- `database` service is PostgreSQL and is isolated from the application container.
- `backend` service is built from the local `backend/` folder and bind mounted for live development.

## Why Docker is used

Docker creates consistent development environments and isolates dependencies.
It ensures the backend and database run the same way across different machines.

## Backend Docker notes

- `services` define containerized components, such as `backend` and `database`.
- `volumes` persist data and avoid losing database state when containers restart.
- `networks` allow containers to communicate securely by service name.
- `depends_on` ensures the backend container starts after the database service is available.
- bind mounts keep local backend source code in sync with the running container.
- environment variables configure container behavior without hard-coding values.
