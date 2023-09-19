-- Initialize the database.
-- Drop any existing data and create empty tables.
-- 
-- psql "postgresql://flaskrpgadmin:flaskrpgadminpass@localhost:5432/flaskrpg" < flaskrpg/schema-postgresql.sql
-- 

drop table if exists star;
drop table if exists post;
drop table if exists "user";

create table "user" (
  id serial primary key,
  username text unique not null,
  password text not null,
  avatar_mimetype text,
  avatar_content bytea,
  constraint avatar check (
    (avatar_mimetype is null and avatar_content is null)
    or
    (avatar_mimetype is not null and avatar_content is not null)
  )
);

create table post (
  id serial primary key,
  author_id integer not null,
  created timestamp not null default current_timestamp,
  title text not null,
  body text not null,
  foreign key (author_id) references "user"(id) on delete cascade
);

create table star (
  user_id integer not null,
  post_id integer not null,
  primary key(user_id, post_id),
  foreign key(user_id) references "user"(id) on delete cascade,
  foreign key(post_id) references post(id) on delete cascade
);
