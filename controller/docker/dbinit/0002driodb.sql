create database drio;

\connect drio

create schema accounts;

\set maxnamelen      256
\set countrycodelen  2
\set maxemaillen     1024
\set maxsecretlen    128
\set maxurllen       1024
\set maxiplen        64
\set maxschemalen    32

create domain drioname      varchar(:maxnamelen);
create domain driocountry   varchar(:countrycodelen);
create domain drioemail     varchar(:maxemaillen);
create domain driosecret    varchar(:maxsecretlen);
create domain driourl       varchar(:maxurllen);
create domain drioip        varchar(:maxiplen);
create domain drioschema    varchar(:maxschemalen);

create or replace function accounts.trigger_insert_account() returns trigger as $insert_account$
    begin
        if nullif(new.schema_name, '') is null then
            new.schema_name = concat('drio_schema_', new.schema_id::text);
        end if;

        return new;
    end;
$insert_account$ language plpgsql;

create or replace function accounts.trigger_update_account() returns trigger as $update_account$
    begin
        new.created_at = old.created_at;
        new.schema_name = old.schema_name;
        new.schema_id = old.schema_id;
        new.updated_at = now();
        return new;
    end;
$update_account$ language plpgsql;

create table if not exists accounts.current (
    id               uuid default gen_random_uuid() primary key,
    name             drioname not null unique check (length(name) >= 1),
    created_at       timestamptz not null default now(),
    updated_at       timestamptz not null default now(),
    country          driocountry not null check (length(country) = :countrycodelen),
    state            drioname not null check (length(state) >= 1),
    city             drioname not null check (length(city) >= 1),
    schema_id        bigserial unique,
    schema_name      drioschema not null unique check (schema_name ~* concat('^', 'drio_schema_', '[0-9]+$')),
    details          jsonb
);

create table if not exists accounts.deleted (
    id               uuid default gen_random_uuid() primary key,
    name             drioname not null unique check (length(name) >= 1),
    created_at       timestamptz not null default now(),
    updated_at       timestamptz not null default now(),
    deleted_at       timestamptz not null default now(),
    country          driocountry not null check (length(country) = :countrycodelen),
    state            drioname not null check (length(state) >= 1),
    city             drioname not null check (length(city) >= 1),
    schema_id        bigserial unique,
    schema_name      drioschema not null unique check (schema_name ~* concat('^', 'drio_schema_', '[0-9]+$')),
    details          jsonb
);

create trigger insert_account
before insert on accounts.current
for each row
execute procedure accounts.trigger_insert_account();

create trigger update_account
before update on accounts.current
for each row
execute procedure accounts.trigger_update_account();
