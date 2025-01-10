from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import json

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Для работы с сессиями

TASKS_FILE = "tasks.json"

# Загрузка задач из файла
def load_tasks():
    try:
        with open(TASKS_FILE, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return []

# Сохранение задач в файл
def save_tasks(tasks):
    with open(TASKS_FILE, "w") as file:
        json.dump(tasks, file, indent=4)

# Переключение темы
@app.route("/toggle_theme")
def toggle_theme():
    if "dark_mode" in session:
        session.pop("dark_mode")
    else:
        session["dark_mode"] = True
    return redirect(request.referrer or url_for("index"))

@app.route("/")
def index():
    tasks = load_tasks()
    sort_by = request.args.get("sort_by", "")

    # Сортировка задач
    if sort_by == "urgency":
        tasks.sort(key=lambda x: x.get("urgency", ""))
    elif sort_by == "importance":
        tasks.sort(key=lambda x: x.get("importance", ""))
    elif sort_by == "both":
        tasks.sort(key=lambda x: (x.get("urgency", ""), x.get("importance", "")))

    return render_template("index.html", tasks=tasks, sort_by=sort_by, dark_mode="dark_mode" in session)

@app.route("/add", methods=["POST"])
def add_task():
    task_text = request.form.get("task")
    category = request.form.get("category", "General")
    urgency = request.form.get("urgency", "1")  # Дефолтное значение для срочности
    importance = request.form.get("importance", "2")  # Дефолтное значение для важности

    if task_text:
        tasks = load_tasks()
        tasks.append({
            "task": task_text,
            "category": category,
            "urgency": urgency,
            "importance": importance
        })
        save_tasks(tasks)
    return redirect(url_for("index"))

@app.route("/delete/<int:task_id>")
def delete_task(task_id):
    tasks = load_tasks()
    if 0 <= task_id < len(tasks):
        tasks.pop(task_id)
        save_tasks(tasks)
    return redirect(url_for("index"))

@app.route("/edit/<int:task_id>", methods=["GET", "POST"])
def edit_task(task_id):
    tasks = load_tasks()
    if request.method == "GET":
        if 0 <= task_id < len(tasks):
            task = tasks[task_id]
            return render_template("edit.html", task=task, task_id=task_id, dark_mode="dark_mode" in session)
        return redirect(url_for("index"))
    elif request.method == "POST":
        if 0 <= task_id < len(tasks):
            task = tasks[task_id]
            task["task"] = request.form.get("task", task["task"])
            task["category"] = request.form.get("category", task.get("category", "General"))
            task["urgency"] = request.form.get("urgency", task.get("urgency", "1"))
            task["importance"] = request.form.get("importance", task.get("importance", "2"))
            save_tasks(tasks)
        return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)