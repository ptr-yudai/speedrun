create table if not exists user (
    id text primary key,
    username text unique,
    password text
);

create table if not exists session (
    user_id text,
    session_id text primary key,
    expired_at integer,

    FOREIGN KEY(user_id) REFERENCES user(id)
);

create table if not exists challenge (
    id text primary key,
    is_open integer
);

create table if not exists attempt (
    id text primary key,
    user_id text,
    challenge_id text,
    start_at integer,
    finish_at integer,

    FOREIGN KEY(user_id) REFERENCES user(id),
    FOREIGN KEY(challenge_id) REFERENCES challenge(id)
);
