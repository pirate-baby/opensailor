#!/bin/bash
uv sync && \
uv run python app/manage.py migrate && \
uv run python app/manage.py collectstatic --noinput && \
uv run gunicorn app.webapp.wsgi:application --bind 0.0.0.0:8000