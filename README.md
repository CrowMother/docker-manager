
# Docker Manager Web App

This is a Flask-based web application for managing Docker containers with user-specific access and label-based file upload functionality.

## Features

- User authentication with roles (admin/user)
- Admin panel for managing users
- Upload files to containers based on Docker label mappings
- Role-based visibility into containers
- Docker container start/stop/restart controls
- Persistent file uploads to volume paths using container labels

## Project Structure

- `app.py`: Flask app entry point and route registration
- `modules/`: Core logic (auth, upload routes, admin management)
- `templates/`: HTML templates
- `users.db`: SQLite database storing users
- `.env`: App secrets like username/password and Flask secret key
- `docker-compose.yml` / `Dockerfile`: Containerized deployment

## How to Run

```bash
docker-compose up --build
```

Access via: `http://localhost:5000`

## Docker Label Convention

Each container should include a label like:

```yaml
labels:
  permissions.owner: "username1,username2"
  files.tokens: "/app/tokens.json"
```

This allows file uploads to be routed by label rather than hardcoded paths.
