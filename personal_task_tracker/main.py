from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, Request, Depends, Form, HTTPException
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import select
from starlette.middleware.sessions import SessionMiddleware

from database import Base, engine, get_db
from models import User, Task
from auth import hash_password, verify_password

BASE_DIR = Path(__file__).resolve().parent
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Personal Task Tracker")

# For local development. Set SESSION_SECRET in your environment before deployment.
import os
SESSION_SECRET = os.environ.get("SESSION_SECRET", "change-this-development-secret-before-deployment")
app.add_middleware(
    SessionMiddleware,
    secret_key=SESSION_SECRET,
    same_site="lax",
    https_only=os.environ.get("COOKIE_HTTPS_ONLY", "false").lower() == "true",
    max_age=60 * 60 * 24 * 7,
)

app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


def current_user(request: Request, db: Session) -> User | None:
    user_id = request.session.get("user_id")
    if not user_id:
        return None
    return db.get(User, user_id)


def page(request: Request, template: str, context: dict):
    context.update({
        "request": request,
        "user": context.get("user"),
        "theme": request.cookies.get("theme", "light"),
    })
    return templates.TemplateResponse(request=request, name=template, context=context)


@app.get("/", response_class=HTMLResponse)
def home(request: Request, db: Session = Depends(get_db)):
    if current_user(request, db):
        return RedirectResponse("/dashboard", status_code=303)
    return RedirectResponse("/login", status_code=303)


@app.get("/register", response_class=HTMLResponse)
def register_page(request: Request):
    return page(request, "register.html", {"error": None, "user": None})


@app.post("/register", response_class=HTMLResponse)
def register(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...),
    db: Session = Depends(get_db),
):
    username = username.strip()
    if len(username) < 3 or len(username) > 50:
        return page(request, "register.html", {"error": "Username 3 થી 50 અક્ષરનો હોવો જોઈએ.", "user": None})
    if len(password) < 8:
        return page(request, "register.html", {"error": "Password ઓછામાં ઓછા 8 અક્ષરનો હોવો જોઈએ.", "user": None})
    if password != confirm_password:
        return page(request, "register.html", {"error": "બંને password સરખા નથી.", "user": None})
    if db.scalar(select(User).where(User.username == username)):
        return page(request, "register.html", {"error": "આ username પહેલેથી જ છે.", "user": None})

    user = User(username=username, password_hash=hash_password(password))
    db.add(user)
    db.commit()
    return RedirectResponse("/login?registered=1", status_code=303)


@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request, registered: str | None = None):
    return page(request, "login.html", {
        "error": None,
        "registered": registered == "1",
        "user": None,
    })


@app.post("/login", response_class=HTMLResponse)
def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    user = db.scalar(select(User).where(User.username == username.strip()))
    if not user or not verify_password(password, user.password_hash):
        return page(request, "login.html", {
            "error": "Username અથવા password ખોટો છે.",
            "registered": False,
            "user": None,
        })

    request.session.clear()
    request.session["user_id"] = user.id
    return RedirectResponse("/dashboard", status_code=303)


@app.post("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/login", status_code=303)


@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request, db: Session = Depends(get_db)):
    user = current_user(request, db)
    if not user:
        return RedirectResponse("/login", status_code=303)

    tasks = list(db.scalars(
        select(Task).where(Task.user_id == user.id).order_by(Task.created_at.desc())
    ).all())
    return page(request, "dashboard.html", {
        "user": user,
        "tasks": tasks,
        "error": None,
    })


@app.post("/tasks")
def create_task(
    request: Request,
    title: str = Form(...),
    description: str = Form(""),
    db: Session = Depends(get_db),
):
    user = current_user(request, db)
    if not user:
        return RedirectResponse("/login", status_code=303)
    title = title.strip()
    if not title or len(title) > 150:
        tasks = list(db.scalars(select(Task).where(Task.user_id == user.id).order_by(Task.created_at.desc())).all())
        return page(request, "dashboard.html", {
            "user": user, "tasks": tasks,
            "error": "Task title ખાલી ન હોવું જોઈએ અને 150 અક્ષરથી વધુ ન હોવું જોઈએ.",
        })
    task = Task(title=title, description=description.strip(), user_id=user.id)
    db.add(task)
    db.commit()
    return RedirectResponse("/dashboard", status_code=303)


@app.post("/tasks/{task_id}/toggle")
def toggle_task(task_id: int, request: Request, db: Session = Depends(get_db)):
    user = current_user(request, db)
    if not user:
        return RedirectResponse("/login", status_code=303)
    task = db.scalar(select(Task).where(Task.id == task_id, Task.user_id == user.id))
    if task:
        task.is_completed = not task.is_completed
        task.completed_at = datetime.utcnow() if task.is_completed else None
        db.commit()
    return RedirectResponse("/dashboard", status_code=303)


@app.post("/tasks/{task_id}/delete")
def delete_task(task_id: int, request: Request, db: Session = Depends(get_db)):
    user = current_user(request, db)
    if not user:
        return RedirectResponse("/login", status_code=303)
    task = db.scalar(select(Task).where(Task.id == task_id, Task.user_id == user.id))
    if task:
        db.delete(task)
        db.commit()
    return RedirectResponse("/dashboard", status_code=303)


@app.post("/preferences/theme")
def set_theme(request: Request, theme: str = Form(...)):
    if theme not in {"light", "dark"}:
        raise HTTPException(status_code=400, detail="Invalid theme")
    response = RedirectResponse("/dashboard", status_code=303)
    response.set_cookie(
        key="theme", value=theme, max_age=60 * 60 * 24 * 365,
        httponly=True, samesite="lax",
        secure=os.environ.get("COOKIE_HTTPS_ONLY", "false").lower() == "true",
    )
    return response
