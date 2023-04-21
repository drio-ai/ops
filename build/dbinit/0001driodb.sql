create database drio;

\connect drio

create schema accounts;

\set maxnamelen 256
\set countrycodelen 2

create or replace function accounts.trigger_update_timestamp() returns trigger as $update_ts$
    begin
        NEW.updated_at = now();
        return NEW;
    end;
$update_ts$ language plpgsql;

create table if not exists accounts.accounts (
    id               uuid default gen_random_uuid() primary key,
    name             varchar(:maxnamelen) not null check (length(name) >= 1),
    created_at       timestamptz not null default now(),
    updated_at       timestamptz not null default now(),
    country          varchar(:countrycodelen) not null check (length(country) = :countrycodelen),
    state            varchar(:maxnamelen) not null check (length(name) >= 1),
    city             varchar(:maxnamelen) not null check (length(name) >= 1),
    details          jsonb
);

create trigger update_timestamp
before update on accounts.accounts
for each row
execute procedure accounts.trigger_update_timestamp();

create table if not exists accounts.ou (
    id int primary key,
    name varchar
);

create schema config;

create table if not exists config.datasource (
    id int primary key,
    name varchar
);

create table if not exists config.ddx (
    id int primary key,
    name varchar
);
