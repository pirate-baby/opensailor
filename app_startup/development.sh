#!/bin/bash
uv sync && \
# this will fail _after_ it succeeds in migrating, so ignore the error
uv run python app/manage.py migrate auth || true && \
uv run python app/manage.py showmigrations && \
uv run python app/manage.py migrate webapp && \
uv run python app/manage.py showmigrations && \
uv run python app/manage.py migrate && \
uv run python app/manage.py showmigrations && \
uv run python app/manage.py collectstatic --noinput && \
uv run python app/manage.py runserver 0.0.0.0:8000