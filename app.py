from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)


def get_db_connection():
    conn = sqlite3.connect("todo.db")
    conn.row_factory = sqlite3.Row
    return conn


def create_table():
    conn = get_db_connection()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS todos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task TEXT NOT NULL,
            completed INTEGER DEFAULT 0
        )
    """)

    conn.commit()
    conn.close()


@app.route("/")
def index():
    conn = get_db_connection()

    todos = conn.execute(
        "SELECT * FROM todos ORDER BY id DESC"
    ).fetchall()

    conn.close()

    return render_template("index.html", todos=todos)


@app.route("/add", methods=["POST"])
def add_todo():

    task = request.form["task"]

    if task.strip():
        conn = get_db_connection()

        conn.execute(
            "INSERT INTO todos (task) VALUES (?)",
            (task,)
        )

        conn.commit()
        conn.close()

    return redirect(url_for("index"))


@app.route("/complete/<int:id>")
def complete_todo(id):

    conn = get_db_connection()

    todo = conn.execute(
        "SELECT completed FROM todos WHERE id = ?",
        (id,)
    ).fetchone()

    if todo:
        new_status = 0 if todo["completed"] else 1

        conn.execute(
            "UPDATE todos SET completed = ? WHERE id = ?",
            (new_status, id)
        )

        conn.commit()

    conn.close()

    return redirect(url_for("index"))


@app.route("/delete/<int:id>")
def delete_todo(id):

    conn = get_db_connection()

    conn.execute(
        "DELETE FROM todos WHERE id = ?",
        (id,)
    )

    conn.commit()
    conn.close()

    return redirect(url_for("index"))


if __name__ == "__main__":
    create_table()
    app.run(debug=True)