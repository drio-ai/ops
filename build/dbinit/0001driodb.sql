create database drio;

\connect drio

create schema accounts;

\set maxnamelen      256
\set countrycodelen  2
\set maxemaillen     1024
\set maxsecretlen    128
\set maxurllen       1024
\set maxiplen        64

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
 * not allowing delete in accounts table as long as there are references from organization_units.
 */
create table if not exists accounts.organization_units (
    id               uuid default gen_random_uuid() primary key,
    name             varchar(:maxnamelen) not null check (length(name) >= 1),
    created_at       timestamptz not null default now(),
    updated_at       timestamptz not null default now(),
    account_id       uuid not null,
    country          varchar(:countrycodelen) not null check (length(country) = :countrycodelen),
    state            varchar(:maxnamelen) not null check (length(state) >= 1),
    city             varchar(:maxnamelen) not null check (length(city) >= 1),
    details          jsonb,
    constraint fk_accounts_ou
        foreign key(account_id) references accounts.accounts(id)
);

create trigger update_timestamp
before update on accounts.organization_units
for each row
execute procedure accounts.trigger_update_timestamp();

create table if not exists accounts.users (
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
before update on accounts.users
for each row
execute procedure accounts.trigger_update_timestamp();

create table if not exists accounts.user_associations (
    id               uuid default gen_random_uuid() primary key,
    user_id          uuid not null,
    account_id       uuid not null,
    ou_id            uuid not null,
    constraint fk_accounts_user_association
        foreign key(account_id) references accounts.accounts(id),
        foreign key(ou_id) references accounts.organization_units(id),
        foreign key(user_id) references accounts.users(id)
);

create schema ddx;

create or replace function ddx.trigger_update_timestamp() returns trigger as $update_ts$
    begin
        NEW.updated_at = now();
        return NEW;
    end;
$update_ts$ language plpgsql;

create table if not exists ddx.clusters (
    id               uuid default gen_random_uuid() primary key,
    name             varchar(:maxnamelen) not null check (length(name) >= 1),
    created_at       timestamptz not null default now(),
    updated_at       timestamptz not null default now(),
    account_id       uuid not null,
    ou_id            uuid not null,
    secret           varchar(:maxsecretlen) not null check (length(secret) >= 32),
    twofa            boolean not null,
    twofaurl         varchar(:maxurllen),
    details          jsonb,
    constraint fk_ddx_clusters
        foreign key(account_id) references accounts.accounts(id),
        foreign key(ou_id) references accounts.organization_units(id),
    constraint fk_twofaurl
        check ((not twofa) or ((twofaurl is not null) and (length(twofaurl) >= 1)))
);

create trigger update_timestamp
before update on ddx.clusters
for each row
execute procedure ddx.trigger_update_timestamp();

create type instance_state as enum ('active', 'inactive', 'failed');

create table if not exists ddx.instances (
    id               uuid default gen_random_uuid() primary key,
    name             varchar(:maxnamelen) not null check (length(name) >= 1),
    created_at       timestamptz not null default now(),
    updated_at       timestamptz not null default now(),
    ddx_cluster_id   uuid not null,
    ipaddress        varchar(:maxiplen) not null check (length(ipaddress) >= 1),
    state            instance_state not null,
    details          jsonb,
    constraint fk_ddx_instances
        foreign key(ddx_cluster_id) references ddx.clusters(id)
);

create schema config;
