# Notes API — Flask Backend with JWT Authentication

A RESTful API built with **Flask** that powers a note-taking application. It provides secure user authentication via **JSON Web Tokens (JWT)** and full CRUD operations for notes, all scoped to the authenticated user.

## Tech Stack

| Technology | Purpose |
|------------|---------|
| **Flask** | Web framework |
| **Flask-SQLAlchemy** | ORM & database management |
| **Flask-Migrate** | Database migrations (Alembic) |
| **Flask-JWT-Extended** | JWT-based authentication |
| **Flask-Bcrypt** | Password hashing |
| **Flask-Marshmallow** | Object serialization / deserialization |
| **Flask-CORS** | Cross-Origin Resource Sharing |
| **SQLite** | Development database |

---

## Setup & Installation

### 1. Clone the repository (if not done already)

```bash
cd client-with-jwt/server
```

### 2. Create and activate a virtual environment

```bash
pipenv install
pipenv shell
```

### 3. Run database migrations

```bash
flask db upgrade
```

### 4. (Optional) Seed the database with sample data

```bash
python seed.py
```

This creates three users:
| Username | Password |
|----------|----------|
| `john` | `password123` |
| `alice` | `password456` |
| `admin` | `admin123` |

Each user has one or more sample notes.

### 5. Start the development server

```bash
python app.py
```

The server starts on **http://localhost:5555**.

---

## API Endpoints

### Authentication

| Method | Endpoint | Auth Required | Description |
|--------|----------|---------------|-------------|
| `POST` | `/signup` | No | Create a new user account |
| `POST` | `/login` | No | Log in and receive a JWT token |
| `GET` | `/me` | Yes | Get the currently authenticated user |

### Notes (protected — requires JWT)

| Method | Endpoint | Auth Required | Description |
|--------|----------|---------------|-------------|
| `GET` | `/notes` | Yes | List user's notes (paginated) |
| `POST` | `/notes` | Yes | Create a new note |
| `GET` | `/notes/<id>` | Yes | Get a single note |
| `PATCH` | `/notes/<id>` | Yes | Update a note |
| `DELETE` | `/notes/<id>` | Yes | Delete a note |

---

## Authentication Flow

### Signup

**Request:**
```json
POST /signup
{
  "username": "jane",
  "password": "securepassword",
  "password_confirmation": "securepassword"
}
```

**Response (201):**
```json
{
  "token": "eyJhbGciOiJIUzI1NiIs...",
  "user": {
    "id": 4,
    "username": "jane"
  }
}
```

### Login

**Request:**
```json
POST /login
{
  "username": "jane",
  "password": "securepassword"
}
```

**Response (200):**
```json
{
  "token": "eyJhbGciOiJIUzI1NiIs...",
  "user": {
    "id": 4,
    "username": "jane"
  }
}
```

### Authenticated Requests

All protected endpoints require the JWT token in the `Authorization` header:

```
Authorization: Bearer <your_jwt_token>
```

### Get Current User

**Request:**
```
GET /me
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

**Response (200):**
```json
{
  "id": 4,
  "username": "jane"
}
```

---

## Notes API

### List Notes (Paginated)

**Request:**
```
GET /notes?page=1&per_page=10
Authorization: Bearer <token>
```

**Response (200):**
```json
{
  "notes": [
    {
      "id": 1,
      "title": "Welcome to Notes",
      "content": "This is your first note!",
      "user_id": 1,
      "user": {
        "id": 1,
        "username": "john"
      },
      "created_at": "2025-01-01T12:00:00+00:00",
      "updated_at": "2025-01-01T12:00:00+00:00"
    }
  ],
  "pagination": {
    "page": 1,
    "per_page": 10,
    "total": 5,
    "pages": 1
  }
}
```

**Query Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `page` | integer | 1 | Page number |
| `per_page` | integer | 10 | Items per page (max 100) |

### Create a Note

**Request:**
```json
POST /notes
Authorization: Bearer <token>

{
  "title": "My New Note",
  "content": "This is the content of my note."
}
```

**Response (201):**
```json
{
  "id": 6,
  "title": "My New Note",
  "content": "This is the content of my note.",
  "user_id": 1,
  "user": {
    "id": 1,
    "username": "john"
  },
  "created_at": "2025-01-15T10:30:00+00:00",
  "updated_at": "2025-01-15T10:30:00+00:00"
}
```

### Get a Single Note

```
GET /notes/1
Authorization: Bearer <token>
```

### Update a Note

```json
PATCH /notes/1
Authorization: Bearer <token>

{
  "title": "Updated Title",
  "content": "Updated content"
}
```

> Both `title` and `content` are optional in a PATCH request — only the provided fields will be updated.

### Delete a Note

```
DELETE /notes/1
Authorization: Bearer <token>
```

**Response (200):**
```json
{
  "message": "Note deleted successfully"
}
```

---

## Error Responses

All errors follow a consistent format:

```json
{
  "errors": ["Human-readable error message"]
}
```

### Common HTTP Status Codes

| Code | Meaning |
|------|---------|
| **200** | Success |
| **201** | Created successfully |
| **401** | Unauthorized — invalid or missing JWT token |
| **404** | Resource not found |
| **422** | Validation error — invalid input data |

---

## Database Models

### User

| Column | Type | Constraints |
|--------|------|-------------|
| `id` | Integer | Primary key, auto-increment |
| `username` | String(80) | Unique, not null |
| `_password_hash` | String(128) | Not null (hashed via bcrypt) |

**Relationships:**
- Has many `Note` records (cascade delete)

### Note

| Column | Type | Constraints |
|--------|------|-------------|
| `id` | Integer | Primary key, auto-increment |
| `title` | String(200) | Not null |
| `content` | Text | Nullable |
| `user_id` | Integer | Foreign key → `users.id`, not null |
| `created_at` | DateTime | Auto-set on creation |
| `updated_at` | DateTime | Auto-updated on modification |

---

## Project Structure

```
server/
├── app.py          # Flask app initialization, routes, and CORS config
├── extensions.py   # Flask extension instances (db, migrate, jwt, bcrypt, ma)
├── models.py       # SQLAlchemy models (User, Note)
├── schema.py       # Marshmallow schemas for serialization
├── seed.py         # Database seeder with sample data
├── Pipfile         # Python dependency manifest
├── Pipfile.lock    # Locked dependency versions
├── .gitignore      # Git ignore rules
├── instance/       # SQLite database file (auto-created)
├── migrations/     # Alembic migration files
└── README.md       # This file
```

---

## Configuration

Key configuration values (set in `app.py`):

| Setting | Value |
|---------|-------|
| `SQLALCHEMY_DATABASE_URI` | `sqlite:///app.db` |
| `JWT_SECRET_KEY` | `super-secret-key-change-in-production` |

> **Important:** Change the `JWT_SECRET_KEY` to a strong, random value before deploying to production.

### CORS

CORS is enabled for the following origins:
- `http://localhost:3000` (React development server)
- `http://localhost:4000` (alternative frontend port)

Credentials are supported (`supports_credentials=True`).

---

## Running Tests

Start the server:

```bash
python app.py
```

The API will be available at **http://localhost:5555**. You can test endpoints using tools like [curl](https://curl.se/), [Postman](https://www.postman.com/), or the React frontend in `client-with-jwt/`.
