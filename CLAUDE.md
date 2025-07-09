# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Docker-based Development
The project uses Docker Compose for development. All development commands are run through Docker containers:

- **Start development environment**: `docker compose up app`
- **Run tests**: `docker compose run --rm test`
- **Format code**: `docker compose run --rm format`
- **Lint code**: `docker compose run --rm lint`
- **Create migrations**: `docker compose run --rm makemigrations`
- **Apply migrations**: `docker compose run --rm migrate`
- **Build frontend assets**: `docker compose run --rm --profile build frontend`
- **Infrastructure management**: `docker compose run --rm --profile deploy opentofu`

### Testing
- Run all tests: `docker compose run --rm test`
- Tests are located in the `tests/` directory
- Uses pytest with django integration (`pytest-django`)
- Test command runs with `--it` flag for integration tests

### Code Quality
- **Linting**: Uses `prospector` with Django profile (`.prospector.yaml`)
- **Formatting**: Uses `black` for Python code formatting
- **Python version**: Requires Python 3.12+

## Architecture Overview

### Project Structure
OpenSailor.org is a Django-based sailing database application with the following key components:

- **Django Backend** (`app/webapp/`): Main application logic
- **Frontend Assets** (`client_side_js/`): JavaScript build pipeline using Vite
- **Infrastructure** (`opentofu/`): OpenTofu (Terraform) infrastructure as code
- **Docker Setup**: Multi-container development environment

### Core Models
The application centers around sailing-related data models:

- **Sailboat**: Core sailboat designs with attributes and images
- **Vessel**: Individual boat instances based on sailboat designs
- **User**: Custom user model with authentication
- **Attribute/SailboatAttribute**: Flexible attribute system for boat specifications
- **VesselNote**: Messaging system for vessel communication
- **Make/Designer**: Boat manufacturer and designer information
- **Media**: File/image management with S3 storage

### Key Features
- **Authentication**: Django Allauth with Google, GitHub, and Facebook social auth
- **Permissions**: Django Guardian for object-level permissions
- **File Storage**: AWS S3 integration for media files (with MinIO for local dev)
- **API**: Django Ninja for REST API endpoints
- **Frontend**: HTMX for dynamic UI updates, Milkdown editor integration
- **Database**: PostgreSQL with migrations

### Technology Stack
- **Backend**: Django 5.2+, PostgreSQL, Redis (implied)
- **Frontend**: HTMX, TailwindCSS, Milkdown editor, Vite build system
- **Storage**: S3-compatible storage (AWS S3 production, MinIO development)
- **Deployment**: Docker, AWS ECS, OpenTofu infrastructure
- **Authentication**: Django Allauth with multiple social providers

### Development Environment
The application runs in Docker containers with:
- **app**: Main Django application (port 8000)
- **database**: PostgreSQL 16
- **minio**: S3-compatible object storage for development
- **nginx**: Reverse proxy
- **frontend**: Node.js container for building client-side assets

### Deployment
- **Production**: AWS ECS with automated deployment via GitHub releases
- **Infrastructure**: Managed via OpenTofu (Terraform fork)
- **Releases**: Create versioned releases (format: `v#.#.#`) to trigger deployments
- **CI/CD**: GitHub Actions for automated builds and deployments

### Configuration
- Environment variables managed through Docker Compose
- Settings split between development and production environments
- Database connections, S3 configuration, and social auth configured via environment variables
- Debug mode controlled by `ENVIRONMENT` variable

### Important Notes
- Custom user model is used (`webapp.User`)
- Object-level permissions implemented with Django Guardian
- Media files stored in S3 with public-read ACL
- Email verification required for account signup
- HTMX used for dynamic frontend interactions without full page reloads

## Critical Development Principles

### When Asked to "Fix" Something
**ALWAYS follow this approach:**

1. **Investigate first** - Understand what's broken and why before making any changes
2. **Make the smallest possible fix** - Only change what needs to be changed to solve the specific problem
3. **Never rewrite working code** - If I'm making large changes or rewriting functionality, I'm probably doing something wrong

**Key insight:** When something that was working suddenly breaks without code changes, look for what changed externally (versions, dependencies, environment) and make the minimal fix to restore the working state.

**If I catch myself wanting to rewrite or make major changes to fix something, STOP and ask: "What is the actual root cause, and what's the smallest change to fix it?"**