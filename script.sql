create table user (
    id integer primary key autoincrement,
    name string not null,
    password string not null
);

create table question (
    id integer primary key autoincrement,
    title string not null,
    explanation string,
    user_id integer not null
);

create table answer (
    id integer primary key autoincrement,
    explanation string not null,
    user_id integer not null,
    question_id integer not null
)