# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [Unreleased]

### Changed
- Standardized codebase language to English — all comments, docstrings, error messages and log statements translated across `emotion_service.py`, `consumer.py`, `redis.py`, `database.py`, `emotion.py`, `emotion_type.py`
- Replaced `FER` + `TensorFlow` ML stack with direct ONNX Runtime inference using `ml-model/emotion_model.onnx`
- `EmotionService` class refactored to use ONNX Runtime — `_detect_face` and `_predict` as private methods, model and Haar Cascade loaded in `__init__`
- `consumer.py` unchanged in structure — still instantiates `EmotionService` and calls `process_emotion`
- Dockerfile now uses `uv` for dependency installation via multi-stage build with a dedicated venv at `/app/.venv`
- Dockerfile runtime stage cleaned up — removed `ffmpeg`, `libfreetype6`, `libsm6`, `libxext6`, `libjpeg62-turbo`, `libpng16-16` (no longer needed without TensorFlow)
- Dockerfile `CMD` no longer uses `--reload` (not appropriate for production)
- `docker-compose.yaml` — added `healthcheck` to both `web` and `db` services
- `docker-compose.yaml` — `web` service now has `restart: on-failure` and waits for `db` to be healthy via `condition: service_healthy`

### Added
- Automated testing suite using `pytest` (located in `tests/` directory)
- Testing dependencies in `requirements.txt` (`pytest`, `pytest-asyncio`, `pytest-mock`, `httpx`)
- `EMOTION_MODEL_PATH` setting in `app/settings.py` — configurable via environment variable, defaults to `ml-model/emotion_model.onnx`
- `HEALTHCHECK` instruction added to `Dockerfile`
- Face detection using OpenCV built-in Haar Cascade (`haarcascade_frontalface_default.xml`) — zero extra dependencies
- Database migration tasks to `mise.toml` (`migrate`, `makemigrations`).
- Automated database migrations on startup for both Docker (via `entrypoint.sh`) and local development (via `mise run dev`).
- Documentation for database migrations in `README.md`.

### Fixed
- Fixed `KeyError: 'angry'` in `EmotionService` by using the standard Enum value constructor `EmotionTypeEnum(value)` instead of member selection.
- Fixed `UnicodeDecodeError` in Redis consumer by adding a safeguard for non-JSON payloads.
- Fixed `alembic/env.py` to remove reference to deleted `EmotionType` model.
- Fixed "uvicorn not found" error in Docker container by adding an anonymous volume for `/app/.venv` in `docker-compose.yaml`.
- Fixed Redis connection issues in Docker by adding a dedicated `redis` service and updating configuration to use internal network.
- Improved `consume_frames` robustness with a connection retry loop (ping) to ensure Redis is available before processing.
- Added input/output monitoring logs to Redis consumer for better observability.

### Changed
- Migrated `EmotionType` from a database table to a Python `Enum` (`EmotionTypeEnum`) to simplify the schema and improve performance.
- Refactored `EmotionService` to remove unnecessary database lookups for emotion types.

### Removed
- Removed `emotion_types` table and its corresponding model `app/models/emotion_type.py`.

### Removed
- `fer` dependency
- `tensorflow` dependency
- `moviepy` dependency
- `opencv-contrib-python-headless` dependency
- `Pillow` dependency
