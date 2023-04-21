create database drio;

\connect drio

create schema accounts;

\set maxnamelen 256
\set countrycodelen 2
\set maxemaillen 1024

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
    state            varchar(:maxnamelen) not null check (length(state) >= 1),
    city             varchar(:maxnamelen) not null check (length(city) >= 1),
    details          jsonb
);

create trigger update_timestamp
before update on accounts.accounts
for each row
execute procedure accounts.trigger_update_timestamp();

/*
 * We will define no action for foreign key constraint. We are starting off with
 * not allowing delete in accounts table as long as there are references from ou.
 */
create table if not exists accounts.ou (
    id               uuid default gen_random_uuid() primary key,
    name             varchar(:maxnamelen) not null check (length(name) >= 1),
    created_at       timestamptz not null default now(),
    updated_at       timestamptz not null default now(),
    account_id       uuid not null,
    country          varchar(:countrycodelen) not null check (length(country) = :countrycodelen),
    state            varchar(:maxnamelen) not null check (length(state) >= 1),
    city             varchar(:maxnamelen) not null check (length(city) >= 1),
    details          jsonb,
    constraint fk_accounts
        foreign key(account_id)
            references accounts.accounts(id)
);

create trigger update_timestamp
before update on accounts.ou
for each row
execute procedure accounts.trigger_update_timestamp();

create table if not exists accounts.user (
    id               uuid default gen_random_uuid() primary key,
    first_name       varchar(:maxnamelen) not null check (length(first_name) >= 1),
    last_name        varchar(:maxnamelen) not null check (length(last_name) >= 1),
    created_at       timestamptz not null default now(),
    updated_at       timestamptz not null default now(),
    email            varchar(:maxemaillen) not null check (length(email) >= 1),
    country          varchar(:countrycodelen) not null check (length(country) = :countrycodelen),
    state            varchar(:maxnamelen) not null check (length(state) >= 1),
    city             varchar(:maxnamelen) not null check (length(city) >= 1),
    active           boolean not null,
    scope            jsonb,
    details          jsonb
);

create trigger update_timestamp
before update on accounts.user
for each row
execute procedure accounts.trigger_update_timestamp();

create schema config;

create table if not exists config.datasource (
    id int primary key,
    name varchar
);

create table if not exists config.ddx (
    id int primary key,
    name varchar
);
