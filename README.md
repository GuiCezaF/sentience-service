# Sentience Service

Sentience Service is a high-performance, asynchronous emotion detection microservice built with **FastAPI**. It processes video frames in real-time using **ONNX Runtime** and provides automated insights via **Redis Pub/Sub**.

## 🚀 Key Features

- **Real-Time Processing**: Event-driven architecture using Redis lists for frame ingestion.
- **Optimized ML Inference**: Utilizes **ONNX Runtime** for lightweight and fast emotion classification (~10MB model) and **OpenCV Haar Cascades** for efficient face detection.
- **Modern Python Stack**: Powered by **Python 3.12**, **uv** for package management, and **mise** for task orchestration.
- **Persistence Layer**: Structured storage of emotional data using **PostgreSQL** and **SQLAlchemy**.
- **Containerized**: Production-ready **Docker** environment with multi-stage builds and health checks.
- **Reliable Coverage**: Comprehensive test suite with 100% infrastructure isolation using mocks.

## 🛠️ Tech Stack

- **Framework**: [FastAPI](https://fastapi.tiangolo.com/)
- **Database**: [PostgreSQL](https://www.postgresql.org/) with [SQLAlchemy](https://www.sqlalchemy.org/)
- **Messaging**: [Redis](https://redis.io/) (List & Pub/Sub)
- **ML Engine**: [ONNX Runtime](https://onnxruntime.ai/) & [OpenCV](https://opencv.org/)
- **Package Manager**: [uv](https://github.com/astral-sh/uv)
- **Environment**: [mise](https://mise.jdx.dev/) & Docker

## 📋 Prerequisites

Before you begin, ensure you have the following installed:
- [Python 3.12+](https://www.python.org/)
- [uv](https://github.com/astral-sh/uv) (for dependency management)
- [mise](https://mise.jdx.dev/) (optional, for task automation)
- [Docker & Docker Compose](https://www.docker.com/)

## ⚙️ Setup & Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/GuiCezaF/sentience-service.git
   cd sentience-service
   ```

2. **Configure Environment Variables**:
   Create a `.env` file based on the provided variables:
   ```env
   DATABASE_URL=postgresql://postgres:postgres@localhost:5433/emotion
   REDIS_URL=redis://localhost:6379
   EMOTION_MODEL_PATH=ml-model/emotion_model.onnx
   DEBUG=true
   ```

3. **Install Dependencies**:
   Using `uv`:
   ```bash
   uv pip install -r requirements.txt
   ```

## 🗄️ Database Migrations

This project uses **Alembic** for database schema management.

### Using mise (Recommended)
```bash
# Generate a new migration after model changes
# Use -m "message" to specify a description
mise run makemigrations --message "description of changes"

# Apply all pending migrations
mise run migrate
```

### Using Alembic directly
```bash
# Generate a new migration
uv run alembic revision --autogenerate -m "description"

# Apply migrations
uv run alembic upgrade head
```


## 🏃 Running the Application

### Using mise (Recommended)
You can run the service directly using the predefined tasks:
```bash
# Start the development server (uvicorn)
mise run dev
```

### Using Docker Compose
To spin up the entire infrastructure (Database, Redis, and API):
```bash
docker-compose up --build
```

### Manual Run
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## 🧪 Testing

The project includes a robust testing suite that mocks all external dependencies (Redis, DB, ONNX).

### Run Tests via mise
```bash
mise run pytest
```

### Run Tests via uv
```bash
$env:PYTHONPATH="."  # Windows
python -m pytest
```

## 📁 Project Structure

```text
├── app/
│   ├── core/           # Logic for Redis and data consumers
│   ├── db/             # Database configuration and session management
│   ├── models/         # SQLAlchemy database models
│   ├── routes/         # API endpoints (FastAPI routers)
│   ├── services/       # Business logic and ML inference (EmotionService)
│   ├── types/          # Pydantic schemas and enums
│   └── utils/          # Utility functions (Base64 conversion, etc.)
├── ml-model/           # Pre-trained ONNX models
├── tests/              # Automated test suite
└── Dockerfile          # Multi-stage production Docker configuration
```

## 📜 License

Distributed under the MIT License. See `LICENSE` for more information.
