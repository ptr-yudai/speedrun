from flask import Flask, session, jsonify, request, send_file
from hashlib import sha256
import sqlite3
from datetime import datetime, timedelta
from uuid import uuid4
from os.path import dirname
import glob
import yaml
from dataclasses import dataclass
from typing import Optional, List, Dict
import traceback

@dataclass
class User:
    id: str
    username: str
    is_runner: bool
    is_admin: bool

@dataclass
class Task:
    id: str
    name: str
    category: str
    description: str
    author: str
    flag: str
    is_open: bool
    is_freezed: bool

@dataclass
class Attempt:
    user_id: str
    task_id: str
    start_at: int
    finish_at: Optional[int]


app = Flask(__name__, static_url_path="", static_folder="./frontend/dist")
app.session_cookie_name = "speedrun"
app.secret_key = "speedrun"
app.config["JSON_AS_ASCII"] = False

# --- util

# sqlite3でdictを返すfactory
def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

def db():
    conn = sqlite3.connect("./database.sqlite")
    conn.row_factory = dict_factory
    return conn

def now():
    return int(datetime.now().timestamp())

def session_expire():
    return int((datetime.now() + timedelta(days=1)).timestamp())

def uuid():
    return str(uuid4())

def select(query, *args):
    conn = db()
    cur = conn.cursor()
    try:
        cur.execute(query, args)
        return cur.fetchone()
    except sqlite3.Error:
        return None
    finally:
        cur.close()
        conn.close()

def select_all(query, *args):
    conn = db()
    cur = conn.cursor()
    try:
        cur.execute(query, args)
        return cur.fetchall()
    except sqlite3.Error:
        return []
    finally:
        cur.close()
        conn.close()

def execute(query, *args):
    conn = db()
    cur = conn.cursor()
    try:
        cur.execute(query, args)
        conn.commit()
    except sqlite3.Error:
        return None
    finally:
        cur.close()
        conn.close()

def error(message):
    return jsonify({"message": message})

# --- user
def h(password):
    return sha256(password.encode()).hexdigest()

def get_login_user_id() -> Optional[str]:
    session_id = session.get("session_id", 0)
    row = select(
        "select user_id from session where session_id = ? AND expired_at > ?",
        session_id,
        now(),
    )
    if row is None:
        return None
    return row["user_id"]

def new_session(user_id):
    session_id = uuid()
    execute(
        "insert into session (user_id, session_id, expired_at) values (?, ?, ?)",
        user_id,
        session_id,
        session_expire(),
    )
    session["session_id"] = session_id

def get_user_by_cred(username, password) -> Optional[User]:
    row = select(
        "select id, username, is_runner, is_admin from user where username = ? AND password = ?",
        username,
        h(password),
    )
    if row is None:
        return None
    return User(
        id=row["id"],
        username=row["username"],
        is_runner=row["is_runner"] != 0,
        is_admin=row["is_admin"] != 0,
    )

def get_user_by_id(user_id) -> Optional[User]:
    row = select(
        "select id, username, is_runner, is_admin from user where id = ?",
        user_id
    )
    if row is None:
        return None
    return User(
        id=row["id"],
        username=row["username"],
        is_runner=row["is_runner"] != 0,
        is_admin=row["is_admin"] != 0,
    )

def do_login(username, password):
    user = get_user_by_cred(username, password)
    if user is None:
        return

    new_session(user.id)
    return user

def get_users_by_ids(userids) -> Dict[str, User]:
    rows = select_all(
        "select id, username, is_runner, is_admin from user where id in ?",
        userids,
    )
    return {row["id"]:User(
        id=row["id"],
        username=row["username"],
        is_runner=row["is_runner"] != 0,
        is_admin=row["is_admin"] != 0,
    ) for row in rows}

def get_all_users() -> Dict[str, User]:
    rows = select_all(
        "select id, username, is_runner, is_admin from user"
    )
    return {row["id"]:User(
        id=row["id"],
        username=row["username"],
        is_runner=row["is_runner"] != 0,
        is_admin=row["is_admin"] != 0,
    ) for row in rows}

# --- tasks
tasks = {}
def load_tasks():
    for path in glob.glob("./tasks/**/task.yml"):
        with open(path) as f:
            data = yaml.safe_load(f)
        data["path"] = dirname(path)
        data["id"] = sha256(data["id"].encode()).hexdigest()
        tasks[data["id"]] = Task(
            id=data["id"],
            name=data["name"],
            category=data["category"],
            description=data["description"],
            flag=data["flag"],
            author=data["author"],
            is_open=False,
            is_freezed=False
        )

def register_tasks():
    # どうせ大した件数はないのでbulk insert面倒だしやらない
    # insert or ignoreですでに存在するtask傷つけない
    for task in tasks.values():
        execute("insert or ignore into task(id, is_open) values (?, ?)", task.id, 0)

def get_task_by_id(task_id) -> Optional[Task]:
    if task_id not in tasks:
        return None

    t = tasks[task_id]
    row = select("select id, is_open, is_freezed from tasks where id = ?", t.id)
    if row is None:
        return None
    t.is_open = (row["is_open"] != 0)
    t.is_freezed = (row["is_freezed"] != 0)
    return t

def get_task_solvers(task_id) -> List[Attempt]:
    solves_data = select_all(
        "select user_id, task_id, start_at, finish_at from attempt where task_id = ? and finish_at is not null",
        task_id,
    )
    solves = []
    for s in solves_data:
        solves.append(Attempt(
            user_id=s["user_id"],
            task_id=s["task_id"],
            start_at=s["start_at"],
            finish_at=s["finish_at"],
        ))
    return solves

def get_user_solved_tasks(user_id) -> List[Attempt]:
    solves_data = select_all(
        "select user_id, task_id, start_at, finish_at from attempt where user_id = ? and finish_at is not null",
        user_id,
    )
    solves = []
    for s in solves_data:
        solves.append(Attempt(
            user_id=s["user_id"],
            task_id=s["task_id"],
            start_at=s["start_at"],
            finish_at=s["finish_at"],
        ))
    return solves


def update_task_status():
    rows = select_all("select id, is_open, is_freezed from task")
    for row in rows:
        tasks[row["id"]].is_open = row["is_open"] != 0
        tasks[row["id"]].is_freezed = row["is_freezed"] != 0

def open_task(task_id):
    execute("update task set is_open = 1 where and task_id = ?", task_id)

def close_task(task_id):
    execute("update task set is_open = 0 where and task_id = ?", task_id)

def freeze_task(task_id):
    execute("update task set is_freezed = 1 where and task_id = ?", task_id)

def unfreeze_task(task_id):
    execute("update task set is_freezed = 0 where and task_id = ?", task_id)

# --- attempt
def get_attempt(user_id, task_id):
    row = select("select user_id, task_id, start_at, finish_at from attempt where user_id = ? AND task_id = ?", user_id, task_id)
    if row is None:
        return None
    return Attempt(
        user_id=row["user_id"],
        task_id=row["task_id"],
        start_at=row["start_at"],
        finish_at=row["fnish_at"],
    )

def get_user_attempts(user_id):
    rows = select_all("select user_id, task_id, start_at, finish_at from attempt where user_id = ?", user_id)
    return [Attempt(
        user_id=row["user_id"],
        task_id=row["task_id"],
        start_at=row["start_at"],
        finish_at=row["fnish_at"],
    ) for row in rows]

def start_attempt(user_id, task_id):
    execute("insert attempt(user_id, task_id, start_at) values (?, ?, ?)", user_id, task_id, now())

def finish_attempt(user_id, task_id):
    execute("update attempt set finish_at = ? where user_id = ? and task_id = ?", now(), user_id, task_id)

def task_viewable(user_id, task: Task):
    """
    おもむろにログイン状態の判定などをする
    """
    if task.is_freezed:
        return True

    attempt = get_attempt(task.id, user_id)
    if attempt:
        return True
    return False

# --- routes
@app.route("/")
def index():
    return send_file("frontend/dist/index.html")


@app.route("/info", methods=["GET"])
def info():
    user_id = get_login_user_id()
    if not user_id:
        return jsonify({})
    user = get_user_by_id(user_id)
    if not user:
        return

    attempts = get_user_attempts(user_id)
    return jsonify({
        "id": user.id,
        "username": user.username,
        "is_runner": user.is_runner,
        "is_admin": user.is_admin,
        "attempts": attempts,
    })

@app.route("/login", methods=["POST"])
def login():
    data = request.get_json() or {}
    username = data.get("username", "")
    password = data.get("password", "")
    if not username or not password:
        return error("username and password are required"), 400

    user = do_login(username, password)
    if user is None:
        return error("login failed"), 400
    return "", 200

@app.route("/register", methods=["POST"])
def register():
    data = request.get_json() or {}
    username = data.get("username", "")
    password = data.get("password", "")
    if not username or not password:
        return error("username and password are required"), 400

    # おもしろ情報
    # うっかりユーザ名もパスワードも同じで登録しようとするとログインになる
    execute("INSERT INTO user(id, username, password) VALUES (?, ?, ?)", uuid(), username, h(password))
    user = do_login(username, password)
    if user is None:
        return error("register failed"), 400
    return "", 200

@app.route("/tasks", methods=["GET"])
def list_tasks():
    update_task_status()

    ts = []
    users = get_all_users()
    for task in tasks.values():
        if not task.is_open:
            continue
        solves = get_task_solvers(task.id)
        ts.append({
            "id": task.id,
            "name": task.name,
            "category": task.category,
            "author": task.author,
            "solves": [{
                "user_id": s.user_id,
                "username": users[s.user_id].username,
                "is_runner": users[s.user_id].is_runner,
                "start_at": s.start_at,
                "finish_at": s.finish_at,
            } for s in solves],
        })

    return jsonify(ts), 200

@app.route("/task/<tid>", methods=["GET"])
def task(tid):
    task = get_task_by_id(tid)
    if task is None:
        return "Not found", 404
    if not task.is_open:
        return "Not found", 404

    user_id = get_login_user_id()
    if not user_id:
        return "Login required to see details", 401

    solves = get_task_solvers(task.id)
    users = get_users_by_ids([s.user_id for s in solves])
    if task_viewable(user_id,task):
        return "clock is not started", 403

    return jsonify({
        "id": task.id,
        "name": task.name,
        "category": task.category,
        "description": task.description,
        "author": task.author,
        "solves": [{
            "user_id": s.user_id,
            "username": users[s.user_id].username,
            "is_runner": users[s.user_id].is_runner,
            "start_at": s.start_at,
            "finish_at": s.finish_at,
        } for s in solves],
    })

@app.route("/task/<tid>/start", methods=["POST"])
def start_task(tid):
    task = get_task_by_id(tid)
    if task is None:
        return "", 404
    if not task.is_open:
        return "", 404

    user_id = get_login_user_id()
    if user_id is None:
        return "", 401
    if task.is_freezed:
        return "", 403

    attempt = get_attempt(user_id, task.id)
    if attempt:
        # already started
        return "", 403
    start_attempt(user_id, task.id)
    return "", 200

@app.route("/task/<tid>/submit", methods=["POST"])
def submit(tid):
    flag = (request.get_json() or {"flag": ""}).get("flag", "").strip()
    task = get_task_by_id(tid)
    if task is None:
        return error("not found"), 404
    if not task.is_open:
        return error("not found"), 404

    user_id = get_login_user_id()
    if not user_id:
        return error("login required"), 401

    attempt = get_attempt(user_id, task.id)
    if not attempt:
        if not task.is_freezed:
            return error("clock has not started"), 403

        app.logger.info("user {} submit flag [{}]".format(user_id, flag))
        # TODO runnerが解いたときになんかする？
        for t in tasks.values():
            if flag == t.flag:
                return jsonify({
                    "solved": True,
                }), 200
        return jsonify({
            "solved": False,
        }), 200

    if attempt.finish_at is not None:
        return error("you already solved"), 403

    app.logger.info("user {} submit flag [{}]".format(user_id, flag))

    # あとでdiscordとかにしてもいいかもね
    # TODO runnerが解いたときになんかする？
    for t in tasks.values():
        if flag == t.flag:
            finish_attempt(user_id, task.id)
            return jsonify({
                "solved": True,
            }), 200
    return jsonify({
        "solved": False,
    }), 200


@app.route("/admin/open/<tid>", methods=["POST"])
def admin_open_task(tid):
    user_id = get_login_user_id()
    if not user_id:
        return "", 401
    user = get_user_by_id(user_id)
    if not user or not user.is_admin:
        return "", 401

    open_task(tid)
    return ""

@app.route("/admin/close/<tid>", methods=["POST"])
def admin_close_task(tid):
    user_id = get_login_user_id()
    if not user_id:
        return "", 401
    user = get_user_by_id(user_id)
    if not user or not user.is_admin:
        return "", 401

    close_task(tid)
    return ""

@app.route("/admin/freeze/<tid>", methods=["POST"])
def admin_freeze_task(tid):
    user_id = get_login_user_id()
    if not user_id:
        return "", 401
    user = get_user_by_id(user_id)
    if not user or not user.is_admin:
        return "", 401

    freeze_task(tid)
    return ""

@app.route("/admin/unfreeze/<tid>", methods=["POST"])
def admin_unfreeze_task(tid):
    user_id = get_login_user_id()
    if not user_id:
        return "", 401
    user = get_user_by_id(user_id)
    if not user or not user.is_admin:
        return "", 401

    unfreeze_task(tid)
    return ""

@app.route("/admin/tasks", methods=["POST"])
def admin_list_tasks():
    user_id = get_login_user_id()
    if not user_id:
        return "", 401
    user = get_user_by_id(user_id)
    if not user or not user.is_admin:
        return "", 401

    update_task_status()
    ts = [ {
        "id": task.id,
        "name": task.name,
        "category": task.category,
        "description": task.description,
        "author": task.author,
        "is_open": task.is_open,
        "is_freezed": task.is_freezed,
    } for task in tasks.values() ]
    return jsonify(ts)



if __name__ == "__main__":

    # テーブル作る
    with open("./schema.sql") as f:
        conn = db()
        cur = conn.cursor()
        cur.executescript(f.read())
        cur.close()
        conn.commit()
        conn.close()

    # task読み込む
    load_tasks()
    register_tasks()

    app.run(debug=True, port=5000, threaded=True)
