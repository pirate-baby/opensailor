#!/bin/bash
uv sync && \
uv run python app/manage.py migrate contenttypes && \
uv run python app/manage.py migrate auth && \
uv run python app/manage.py migrate && \
uv run python app/manage.py collectstatic --noinput && \
uv run gunicorn app.webapp.wsgi:application --bind 0.0.0.0:8000