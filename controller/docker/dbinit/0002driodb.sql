create database drio;

\connect drio

create schema main;

\set maxnamelen      256
\set countrycodelen  2
\set maxemaillen     1024
\set maxsecretlen    128
\set maxurllen       1024
\set maxiplen        64
\set maxschemalen    64

create domain drioname      varchar(:maxnamelen);
create domain driocountry   varchar(:countrycodelen);
create domain drioemail     varchar(:maxemaillen);
create domain driosecret    varchar(:maxsecretlen);
create domain driourl       varchar(:maxurllen);
create domain drioip        varchar(:maxiplen);
create domain drioschema    varchar(:maxschemalen);

create type drioddxinstancestate as enum ('running', 'stopped', 'upgrading', 'failed');

create or replace function main.trigger_insert_account() returns trigger as $insert_account$
    begin
        if nullif(new.schema_name, '') is null then
            new.schema_name = concat('drio_account_', new.schema_id::text);
        end if;

        new.deleted = false;
        return new;
    end;
$insert_account$ language plpgsql;

create or replace function main.trigger_update_account() returns trigger as $update_account$
    begin
        new.created_at = old.created_at;
        new.schema_name = old.schema_name;
        new.schema_id = old.schema_id;
        new.updated_at = now();
        return new;
    end;
$update_account$ language plpgsql;

create table if not exists main.accounts (
    id               uuid default gen_random_uuid() primary key,
    name             drioname not null check (length(name) >= 1),
    created_at       timestamptz not null default now(),
    updated_at       timestamptz not null default now(),
    deleted_at       timestamptz,
    deleted          boolean,
    country          driocountry not null check (length(country) > 1),
    state            drioname not null check (length(state) >= 1),
    city             drioname not null check (length(city) >= 1),
    schema_id        bigserial unique,
    schema_name      drioschema not null unique check (schema_name ~* concat('^', 'drio_account_', '[0-9]+$')),
    details          jsonb
);

create trigger insert_account
before insert on main.accounts
for each row
execute procedure main.trigger_insert_account();

create trigger update_account
before update on main.accounts
for each row
execute procedure main.trigger_update_account();
