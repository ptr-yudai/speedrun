from flask import Flask, session, jsonify, request
from hashlib import sha256
import sqlite3
from datetime import datetime, timedelta
from uuid import uuid4
from os.path import dirname
import glob
import yaml
from dataclasses import dataclass
from typing import Optional, List, Dict

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


app = Flask(__name__, static_url_path="")
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
    finally:
        cur.close()
        conn.close()

def select_all(query, *args):
    conn = db()
    cur = conn.cursor()
    try:
        cur.execute(query, args)
        return cur.fetchall()
    finally:
        cur.close()
        conn.close()

def execute(query, *args):
    conn = db()
    cur = conn.cursor()
    try:
        cur.execute(query, args)
        conn.commit()
    except Exception as e:
        raise e
    finally:
        cur.close()
        conn.close()

# --- user
def h(password):
    return sha256(password.encode()).hexdigest()

def get_login_user_id() -> Optional[str]:
    session_id = session.get("session_id", 0)
    row = select(
        "select user_id from session where session_id = ? AND expired_at < ?",
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

def get_user_by_cred(username, password):
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

def do_login(username, password):
    user = get_user_by_cred(username, password)
    if user is None:
        return

    new_session(user.id)
    return user

def get_usernames(userids) -> Dict[str, str]:
    usernames = select_all("select id, username from user where id in ?", userids)
    return {u["id"]:u["username"] for u in usernames}

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
        execute("insert or ignore into task(id, is_open) values (?, ?)", task["id"], 0)

def get_task_by_id(task_id) -> Optional[Task]:
    if task_id not in tasks:
        return None

    t = tasks[task_id]
    row = select("select id, is_open, is_freezed from tasks where id = ?", t["id"])
    if row is None:
        return None
    t.is_open = (row["is_open"] != 1)
    t.is_freezed = (row["is_freezed"] != 1)
    return t

def get_task_solves(task_id) -> List[Attempt]:
    solves_data = select_all(
        "select user_id, task_id, start_at, finish_at where task_id = ? and finish_at is not null",
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

@app.route("/", methods=["GET"])
def index():
    pass

@app.route("/login", methods=["POST"])
def login():
    data = request.get_json() or {}
    username = data.get("username", "")
    password = data.get("password", "")
    if not username or not password:
        return "", 400

    user = do_login(username, password)
    if user is None:
        return "", 400
    return jsonify({
        "id": user.id,
        "username": user.username,
        "is_runner": user.is_runner,
        "is_admin": user.is_admin,
    })

@app.route("/register", methods=["POST"])
def register():
    data = request.get_json() or {}
    username = data.get("username", "")
    password = data.get("password", "")
    if not username or not password:
        return "", 400

    execute("INSERT INTO user(id, username, password) VALUES (?, ?, ?)", uuid(), username, h(password))
    user = do_login(username, password)
    if user is None:
        return "", 400
    return jsonify({
        "id": user.id,
        "username": user.username,
        "is_runner": user.is_runner,
        "is_admin": user.is_admin,
    })

@app.route("/task/<tid>", methods=["GET"])
def task(tid):
    task = get_task_by_id(tid)
    if task is None:
        return "", 404
    if not task.is_open:
        return "", 404

    user_id = get_login_user_id()
    if not user_id:
        return "", 401
    if not task_viewable(user_id,task):
        return "", 403

    solves = get_task_solves(task.id)
    usernames = get_usernames([s.user_id for s in solves])

    return jsonify({
        "id": task.id,
        "name": task.name,
        "category": task.category,
        "description": task.description,
        "author": task.author,
        "solves": [{
            "user_id": s.user_id,
            "username": usernames[s.user_id],
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
    task = get_task_by_id(tid)
    if task is None:
        return "", 404
    if not task.is_open:
        return "", 404

    user_id = get_login_user_id()
    if not user_id:
        return "", 401
    if not task_viewable(user_id, task):
        return "", 403

    flag = (request.get_json() or {"flag": ""}).get("flag", "").strip()

    # あとでdiscordとかにしてもいいかもね
    app.logger.info("user {} submit flag [{}]".format(user_id, flag))

    # TODO runnerが解いたときになんかする？

    for t in tasks:
        if flag == t.flag:
            False
            return jsonify({
                "solved": True,
            }), 400
    return jsonify({
        "solved": False,
    }), 400


@app.route("/admin/open/<tid>", methods=["POST"])
def open_task(tid):
    pass

@app.route("/admin/freeze/<tid>", methods=["POST"])
def freeze_task(tid):
    pass

@app.route("/admin/tasks", methods=["POST"])
def list_tasks():
    pass

if __name__ == "__main__":
    # task読み込む
    load_tasks()
    register_tasks()

    # テーブル作る
    with open("./schema.sql") as f:
        conn = db()
        cur = conn.cursor()
        cur.executescript(f.read())
        cur.close()
        conn.commit()
        conn.close()

    app.run(debug=True, port=5000, threaded=True)
