create table if not exists user (
    id text primary key,
    username text unique,
    password text,
    is_runner integer default 0,
    is_admin integer default 0
);

create table if not exists session (
    user_id text,
    session_id text primary key,
    expired_at integer,

    FOREIGN KEY(user_id) REFERENCES user(id) ON DELETE CASCADE
);

create table if not exists task (
    id text primary key,
    is_open integer,
    is_freezed integer default 0
);

create table if not exists attempt (
    user_id text,
    task_id text,
    start_at integer,
    finish_at integer,

    PRIMARY KEY (user_id, task_id),
    FOREIGN KEY(user_id) REFERENCES user(id) ON DELETE SET NULL,
    FOREIGN KEY(task_id) REFERENCES task(id) ON DELETE SET NULL
);
