# Production-Ready Blog API Starter

A runnable Flask API example for learning environment configuration, Docker, PostgreSQL,
logging, feature flags, health checks, JWT authentication, and tests.

## 1. Requirements

- Docker Desktop with Docker Compose
- PowerShell on Windows (or a compatible terminal)

## 2. Set secrets before starting

Edit `.env`. Generate two different secret values using:

```powershell
python -c "import secrets; print(secrets.token_hex(32))"
```

Replace `SECRET_KEY`, `JWT_SECRET_KEY`, and `POSTGRES_PASSWORD` in `.env`.
Do not commit `.env` to Git.

## 3. Start the application

From this folder:

```powershell
docker compose config
docker compose up -d --build
docker compose ps
docker compose logs -f web
```

Open `http://127.0.0.1:5000/` or test health:

```powershell
Invoke-RestMethod http://127.0.0.1:5000/health/live
Invoke-RestMethod http://127.0.0.1:5000/health/ready
```

Stop containers without deleting database data:

```powershell
docker compose down
```

Do **not** run `docker compose down -v` unless you intentionally want to delete the
PostgreSQL volume and its data.

## 4. API examples

Register:

```powershell
$body = @{
  username = "demo"
  email = "demo@example.com"
  password = "DemoPassword123!"
} | ConvertTo-Json

Invoke-RestMethod -Method Post `
  -Uri http://127.0.0.1:5000/api/auth/register `
  -ContentType "application/json" -Body $body
```

Login and save the token:

```powershell
$login = @{
  username_or_email = "demo"
  password = "DemoPassword123!"
} | ConvertTo-Json

$result = Invoke-RestMethod -Method Post `
  -Uri http://127.0.0.1:5000/api/auth/login `
  -ContentType "application/json" -Body $login

$token = $result.access_token
```

Create a post:

```powershell
$post = @{
  title = "My first post"
  body = "This post was created using the API."
} | ConvertTo-Json

Invoke-RestMethod -Method Post `
  -Uri http://127.0.0.1:5000/api/posts `
  -Headers @{ Authorization = "Bearer $token" } `
  -ContentType "application/json" -Body $post
```

List posts:

```powershell
Invoke-RestMethod http://127.0.0.1:5000/api/posts
```

Add a comment (replace `1` with a real post ID):

```powershell
$comment = @{ body = "Great post!" } | ConvertTo-Json

Invoke-RestMethod -Method Post `
  -Uri http://127.0.0.1:5000/api/posts/1/comments `
  -Headers @{ Authorization = "Bearer $token" } `
  -ContentType "application/json" -Body $comment
```

## 5. Feature flag

Set `FEATURE_POST_EXPORT=true` in `.env`, then recreate the web container:

```powershell
docker compose up -d --force-recreate web
```

Visit `http://127.0.0.1:5000/api/posts/export.csv`. The route returns CSV only when
the flag is enabled.

## 6. Run tests locally

Create and activate a virtual environment, install requirements, then run:

```powershell
python -m pip install -r requirements.txt
pytest -q
```

## 7. Database migrations

For local learning, development defaults to creating tables automatically.
Staging and production disable automatic table creation. Before deploying those
environments, initialize and commit Flask-Migrate migrations, then run
`flask --app app db upgrade` as a controlled release step. Do not rely on
`db.create_all()` as a production migration strategy.

## 8. Production notes

- `compose.prod.yaml` is a starting point, not a complete public cloud deployment.
- Use a secrets manager and a managed PostgreSQL service in production.
- Put a TLS-enabled reverse proxy or managed ingress in front of the web service.
- Review rate limiting, security headers, backups, monitoring, dependency pinning,
  and migration/rollback procedures before exposing the API to the internet.
- Do not use the development Flask server for production.
