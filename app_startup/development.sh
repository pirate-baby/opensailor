#!/bin/bash
uv sync && \
uv run python app/manage.py migrate && \
uv run python app/manage.py runserver 0.0.0.0:8000