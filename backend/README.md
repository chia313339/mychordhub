# MyChordHub Backend API

A FastAPI-based backend service for the MyChordHub guitar tab editing platform.

## Features

- **User Management**: Registration, authentication, and profile management
- **Song Management**: CRUD operations for guitar songs and chord charts
- **Custom Chords**: User-defined chord diagrams and fingerings
- **Collections**: Song organization and favorites
- **Ratings & Reviews**: Community rating system
- **Music Theory**: Chord transposition, key changes, and capo calculations
- **Search**: Full-text search across songs and metadata
- **API Documentation**: Automatic OpenAPI/Swagger documentation

## Tech Stack

- **Framework**: FastAPI
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Authentication**: JWT tokens
- **Validation**: Pydantic v2
- **Testing**: Pytest
- **Migrations**: Alembic
- **Containerization**: Docker

## Project Structure

```
backend/
├── src/app/
│   ├── api/                 # API endpoints
│   │   └── api_v1/
│   │       ├── endpoints/   # Route handlers
│   │       └── api.py       # Main API router
│   ├── core/                # Core functionality
│   │   ├── config.py        # Configuration
│   │   ├── security.py      # Authentication & security
│   │   ├── middleware.py    # Custom middleware
│   │   └── exceptions.py    # Custom exceptions
│   ├── db/                  # Database configuration
│   ├── models/              # SQLAlchemy models
│   ├── schemas/             # Pydantic schemas
│   ├── services/            # Business logic
│   ├── utils/               # Utility functions
│   └── main.py              # FastAPI application
├── tests/                   # Test files
├── alembic/                 # Database migrations
├── pyproject.toml           # Project dependencies
└── README.md
```

## Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL
- Poetry (for dependency management)

### Installation

1. Clone the repository and navigate to the backend directory:
   ```bash
   cd mychordhub/backend
   ```

2. Install dependencies with Poetry:
   ```bash
   poetry install
   ```

3. Copy environment variables and configure:
   ```bash
   cp .env.example .env
   # Edit .env with your database and other settings
   ```

4. Run database migrations:
   ```bash
   poetry run alembic upgrade head
   ```

5. Start the development server:
   ```bash
   poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

### Using Docker

1. Build and run with Docker Compose:
   ```bash
   docker-compose up --build
   ```

The API will be available at:
- **API**: http://localhost:8000
- **Documentation**: http://localhost:8000/api/v1/docs
- **ReDoc**: http://localhost:8000/api/v1/redoc

## API Endpoints

### Authentication
- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/test-token` - Test authentication

### Users
- `GET /api/v1/users/me` - Get current user
- `PUT /api/v1/users/me` - Update current user

### Songs
- `GET /api/v1/songs/` - List public songs
- `GET /api/v1/songs/search` - Search songs
- `GET /api/v1/songs/my` - Get user's songs
- `POST /api/v1/songs/` - Create song
- `GET /api/v1/songs/{id}` - Get song details
- `PUT /api/v1/songs/{id}` - Update song
- `DELETE /api/v1/songs/{id}` - Delete song

### Collections
- `GET /api/v1/collections/` - List public collections
- `GET /api/v1/collections/my` - Get user's collections
- `POST /api/v1/collections/` - Create collection
- `POST /api/v1/collections/{id}/songs/{song_id}` - Add song to collection

### Music Theory
- `POST /api/v1/music/transpose` - Transpose chords
- `POST /api/v1/music/change-key` - Change song key
- `POST /api/v1/music/capo-suggestion` - Get capo suggestions
- `GET /api/v1/music/validate-chord` - Validate chord name

## Environment Variables

```bash
# Application
SECRET_KEY=your-secret-key
DEBUG=true
PROJECT_NAME=MyChordHub

# Database
POSTGRES_SERVER=localhost
POSTGRES_USER=mychordhub
POSTGRES_PASSWORD=password
POSTGRES_DB=mychordhub
DATABASE_URL=postgresql://mychordhub:password@localhost:5432/mychordhub

# Redis (optional)
REDIS_URL=redis://localhost:6379/0

# CORS
BACKEND_CORS_ORIGINS=["http://localhost:3000"]
```

## Development

### Running Tests

```bash
poetry run pytest
```

### Code Quality

```bash
# Format code
poetry run black .

# Sort imports
poetry run isort .

# Lint
poetry run flake8 .

# Type checking
poetry run mypy .
```

### Database Migrations

```bash
# Create new migration
poetry run alembic revision --autogenerate -m "Description"

# Apply migrations
poetry run alembic upgrade head

# Rollback migration
poetry run alembic downgrade -1
```

## Music Theory Features

The API includes comprehensive music theory utilities:

- **Chord Parsing**: Parse complex chord names (e.g., "Cmaj7/E")
- **Transposition**: Transpose individual chords or progressions
- **Key Changes**: Convert songs between different keys
- **Capo Calculations**: Suggest capo positions for key changes
- **Chord Validation**: Validate chord name syntax
- **Chord Extraction**: Extract chords from lyrics text

## Authentication

The API uses JWT tokens for authentication:

1. Register or login to get an access token
2. Include the token in requests: `Authorization: Bearer <token>`
3. Tokens expire after 8 days (configurable)

## Error Handling

The API includes comprehensive error handling:

- Validation errors return 400 with detailed field information
- Authentication errors return 401
- Authorization errors return 403
- Not found errors return 404
- Server errors return 500 with error tracking

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run tests and ensure they pass
6. Submit a pull request

## License

This project is licensed under the MIT License.