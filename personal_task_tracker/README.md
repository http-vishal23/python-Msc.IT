# Personal Task Tracker (FastAPI)

## Features
- User registration/login/logout
- SQLite persistent storage
- Session-based login state
- Per-user task isolation
- Create, complete/reopen, and delete tasks
- Cookie-based light/dark preference
- Password hashing using PBKDF2-HMAC-SHA256

## Run on Windows
1. Install Python 3.10+.
2. Open Command Prompt/PowerShell in this folder.
3. Create and activate a virtual environment:
   ```powershell
   python -m venv venv
   .\venv\Scripts\activate
   ```
4. Install dependencies:
   ```powershell
   pip install -r requirements.txt
   ```
5. Set a session secret (recommended even for development):
   ```powershell
   $env:SESSION_SECRET = "replace-with-a-long-random-secret"
   ```
6. Run:
   ```powershell
   uvicorn main:app --reload
   ```
7. Open http://127.0.0.1:8000

The SQLite database `tasks.db` is created automatically in the project directory.

## Production notes
- Set a long, random `SESSION_SECRET` using an environment variable.
- Set `COOKIE_HTTPS_ONLY=true` when serving over HTTPS.
- Use HTTPS and add CSRF protection/rate limiting before public deployment.
- SessionMiddleware stores signed session data in a cookie; do not put secrets or sensitive data in it. This app stores only the user ID.
