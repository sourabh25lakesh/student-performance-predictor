# Student Performance Predictor

A production-ready web application that predicts a student's final marks
using a trained Linear Regression model, with full JWT authentication and
MySQL-backed prediction history.

> **Status: End-to-end app complete** — Project structure, MySQL configuration,
> JWT authentication, Linear Regression model training/loading, Prediction API,
> Prediction History API, Dashboard API, and Bootstrap frontend pages are
> complete. Deployment configs can be added next.

---

## Phase 1 Contents

- Full backend project structure (FastAPI, SQLAlchemy, Pydantic)
- MySQL database configuration (via SQLAlchemy + PyMySQL)
- `users` and `predictions` tables (ORM models)
- Complete JWT authentication:
  - `POST /auth/register`
  - `POST /auth/login`
  - `POST /auth/logout`
  - `GET /users/me` (protected route)
- Password hashing with bcrypt (Passlib)
- Centralized configuration via environment variables
- Logging configuration
- CORS configuration
- Synthetic training dataset: `dataset/students.csv` (500 rows)
- Reference SQL schema: `database/schema.sql`

---

## Project Structure (so far)

```
student-performance-predictor/
├── backend/
│   ├── app/
│   │   ├── main.py                 # FastAPI app entrypoint
│   │   ├── core/
│   │   │   ├── config.py           # Settings (env vars)
│   │   │   ├── security.py         # Password hashing + JWT
│   │   │   └── logging_config.py   # Logging setup
│   │   ├── api/
│   │   │   ├── auth.py             # /auth/* routes
│   │   │   └── users.py            # /users/me route
│   │   ├── models/
│   │   │   ├── user.py             # User ORM model
│   │   │   └── prediction.py       # Prediction ORM model
│   │   ├── schemas/
│   │   │   ├── user.py             # Pydantic schemas
│   │   │   └── token.py
│   │   ├── database/
│   │   │   └── database.py         # Engine, session, init_db()
│   │   ├── services/
│   │   │   └── auth_service.py     # Auth business logic
│   │   └── ml/                     # (populated in Phase 2)
│   ├── requirements.txt
│   └── .env.example
├── dataset/
│   └── students.csv                # Training data (Phase 2 uses this)
├── database/
│   └── schema.sql                  # Reference MySQL schema
├── frontend/
│   ├── assets/
│   │   ├── css/style.css
│   │   └── js/app.js
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   ├── predict.html
│   ├── history.html
│   ├── trash.html
│   ├── profile.html
│   └── index.html
├── .gitignore
└── README.md
```

---

## 1. Prerequisites

- Python 3.13+
- MySQL Server 8.0+ running locally or remotely
- `pip` / `venv`

---

## 2. MySQL Setup

Create the database (the app will auto-create tables on first run, but you
need the database itself to exist first):

```sql
CREATE DATABASE student_performance_db
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;
```

Or simply run the reference script:

```bash
mysql -u root -p < database/schema.sql
```

---

## 3. Environment Variables

Copy the example env file and fill in your real values:

```bash
cd backend
cp .env.example .env
```

Key variables in `.env`:

| Variable | Description | Example |
|---|---|---|
| `DB_HOST` | MySQL host | `localhost` |
| `DB_PORT` | MySQL port | `3306` |
| `DB_USER` | MySQL username | `root` |
| `DB_PASSWORD` | MySQL password | `your_password` |
| `DB_NAME` | Database name | `student_performance_db` |
| `DATABASE_URL` | Optional single connection string (overrides DB_* fields) | `mysql+pymysql://user:pass@host:3306/db` |
| `JWT_SECRET_KEY` | Secret used to sign JWTs — **change in production** | long random string |
| `JWT_ALGORITHM` | JWT signing algorithm | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token lifetime | `1440` |
| `CORS_ORIGINS` | Allowed frontend origins | `["*"]` |

---

## 4. Installation

```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

---

## 5. Run the Backend

```bash
cd backend
uvicorn app.main:app --reload
```

- API base URL: `http://127.0.0.1:8000`
- Swagger docs: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

On startup, the app automatically creates the `users` and `predictions`
tables in your MySQL database if they don't already exist.

---

## 6. Run the Frontend

Open a second terminal:

```bash
cd frontend
python3 -m http.server 5500
```

- Frontend URL: `http://127.0.0.1:5500`
- The frontend expects the backend API at `http://127.0.0.1:8000`.
- To change the API URL, edit `frontend/assets/js/app.js`.

---

## 7. Try It Out

**Register:**

```bash
curl -X POST http://127.0.0.1:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"name": "Jane Doe", "email": "jane@example.com", "password": "StrongPass123"}'
```

**Login:**

```bash
curl -X POST http://127.0.0.1:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "jane@example.com", "password": "StrongPass123"}'
```

This returns a JWT `access_token`. Use it to call the protected route:

```bash
curl http://127.0.0.1:8000/users/me \
  -H "Authorization: Bearer <access_token>"
```

---

## Pages

- Login
- Register
- Dashboard
- Predict Marks
- Prediction History
- Trash
- User Profile
- Logout

## What's Next

- Dockerfile, docker-compose.yml, and deployment instructions for
  Render/Railway.

---

## License

This project is provided as-is for educational/demo purposes.
