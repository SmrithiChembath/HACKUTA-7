create extension if not exists "uuid-ossp";

create table if not exists users (
  id uuid primary key default uuid_generate_v4(),
  auth0_sub text unique,
  email text,
  created_at timestamp with time zone default now()
);

create table if not exists sessions (
  id uuid primary key default uuid_generate_v4(),
  user_id uuid references users(id) on delete cascade,
  pack_slug text not null,
  step_index int default 0,
  lang text default 'en',
  created_at timestamp with time zone default now(),
  updated_at timestamp with time zone default now()
);

create table if not exists answers (
  id uuid primary key default uuid_generate_v4(),
  session_id uuid references sessions(id) on delete cascade,
  key text not null,
  value jsonb not null,
  updated_at timestamp with time zone default now(),
  unique(session_id, key)
);

create table if not exists messages (
  id uuid primary key default uuid_generate_v4(),
  session_id uuid references sessions(id) on delete cascade,
  role text not null,
  text text,
  audio_url text,
  meta jsonb,
  created_at timestamp with time zone default now()
);

create table if not exists uploads (
  id uuid primary key default uuid_generate_v4(),
  session_id uuid references sessions(id) on delete cascade,
  kind text not null,
  file_path text,
  doc_json jsonb,
  created_at timestamp with time zone default now()
);
