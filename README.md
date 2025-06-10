# Google Keep Notes Clone APIs

## Overview

Backend clone service for a **Google Keep–style note-taking app**, built with **Django**, **DRF**, and **SQLite**. It provides full CRUD operations for notes, secure user registration/login via JWT, and session management.

## Tech Stack

- **Python** (Django)
- **Django Rest Framework**
- **SQLite** (or configurable with PostgreSQL)
- **JWT** authentication
- **dotenv** for environment variables

## Installation

### Clone Repository

```bash
git clone https://github.com/nia3zzz/google_keep_notes_clone_apis.git
cd google_keep_notes_clone_apis
```

### Install Dependencies

Create and activate a virtual environment (optional but recommended):

```bash
python3 -m venv venv
source venv/bin/activate
```

Then install dependencies:

```bash
pip install -r requirements.txt
```

### Setup Environment Variables

Copy the sample environment configuration:

```bash
cp .env.sample .env
```

Update `.env` with your actual settings (e.g., `SECRET_KEY`, database config, etc.).

### Run Database Migrations

```bash
python manage.py migrate
```

### Start the Server

```bash
python manage.py runserver
```

The server will start at `http://localhost:8000`.

## Usage

- **Base API URL**: `http://localhost:8000/api/v1/`

### User Endpoints

- `POST users/` — Create a new user.
- `GET users/` — Get a user using email.
- `POST users/login/` — Login and receive JWT cookie.
- `POST users/logout/` — Logout user.

### Notes Endpoints

- `POST notes/` — Create a note.
- `GET notes/` — View a specific note.
- `PUT notes/{id}/` — Update a note.
- `DELETE notes/{id}/` — Delete a note.
- `POST notes/collaborators/{id}/` — Add collaborator in a note.
- `DELETE notes/collaborators/{id}/` — Remove collaborator in a note.
