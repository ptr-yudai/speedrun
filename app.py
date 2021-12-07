from flask import Flask, session, jsonify, request
from hashlib import sha256
import sqlite3
from datetime import datetime, timedelta
from uuid import uuid4
from os.path import dirname
import glob
import yaml


app = Flask(__name__, static_url_path="")
app.session_cookie_name = "speedrun"
app.secret_key = "speedrun"
app.config["JSON_AS_ASCII"] = False

challenges = {}
def load_challenges():
    for path in glob.glob("./tasks/**/task.yml"):
        with open(path) as f:
            data = yaml.safe_load(f)
        data["path"] = dirname(path)
        key = sha256(data["name"].encode()).hexdigest()
        challenges[key] = data

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

def insert(query, *args):
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

def get_login_user_id():
    session_id = session.get("session_id", 0)
    user_id = select(
        "select user_id from session where session_id = ? AND expired_at < ?",
        session_id,
        now(),
    )
    return user_id

def new_session(user_id):
    session_id = uuid()
    insert(
        "insert into session (user_id, session_id, expired_at) values (?, ?, ?)",
        user_id,
        session_id,
        session_expire(),
    )
    session["session_id"] = session_id

def h(password):
    return sha256(password.encode()).hexdigest()

def get_user_id(username, password):
    row = select(
        "select id from user where username = ? AND password = ?",
        username,
        h(password),
    )
    print(username, password)
    if row:
        return row["id"]
    return None

def do_login(username, password):
    user_id = get_user_id(username, password)
    if user_id is None:
        return

    new_session(user_id)
    return user_id


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

    user_id = do_login(username, password)
    if user_id is None:
        return "", 400
    return jsonify({"user_id": user_id})

@app.route("/register", methods=["POST"])
def register():
    data = request.get_json() or {}
    username = data.get("username", "")
    password = data.get("password", "")
    if not username or not password:
        return "", 400

    insert("INSERT INTO user(id, username, password) VALUES (?, ?, ?)", uuid(), username, h(password))
    user_id = do_login(username, password)
    if user_id is None:
        return "", 400
    return jsonify({"user_id": user_id})

@app.route("/submit/", methods=["POST"])
def submit():
    pass

@app.route("/start-challenge/<cid>", methods=["POST"])
def start(cid):
    pass

@app.route("/challenge/<cid>", methods=["POST"])
def challenge(cid):
    pass

@app.route("/admin/open/<cid>", methods=["POST"])
def open_challenge(cid):
    pass

@app.route("/admin/freeze/<cid>", methods=["POST"])
def freeze_challenge(cid):
    pass

@app.route("/admin/challenges", methods=["POST"])
def list_challenges():
    pass

if __name__ == "__main__":
    # challenge読み込む
    load_challenges()
    print(challenges)

    # テーブル作る
    with open("./schema.sql") as f:
        conn = db()
        cur = conn.cursor()
        cur.executescript(f.read())
        cur.close()
        conn.commit()
        conn.close()

    app.run(debug=True, port=5000, threaded=True)
