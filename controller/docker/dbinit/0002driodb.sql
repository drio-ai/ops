create database drio;

\connect drio

create extension "uuid-ossp";

create schema main;

\set maxnamelen      256
\set countrycodelen  2
\set maxemaillen     1024
\set maxsecretlen    128
\set maxurllen       1024
\set maxiplen        64
\set maxschemalen    64
\set maxendpointlen  4096

create domain drioname      varchar(:maxnamelen);
create domain driocountry   varchar(:countrycodelen);
create domain drioemail     varchar(:maxemaillen);
create domain driosecret    varchar(:maxsecretlen);
create domain driourl       varchar(:maxurllen);
create domain drioip        varchar(:maxiplen);
create domain drioschema    varchar(:maxschemalen);
create domain drioendpoint  varchar(:maxendpointlen);

create type drioddxinstancestate as enum ('running', 'stopped', 'upgrading', 'failed');

create type drioddxdatasourcetype as enum ('kafka', 'amazon kinesis', 'azure event hub');

create type drioaccountauthprovider as enum ('local', 'microsoft', 'google');

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

/*
 * The name field/column in the main.accounts table must be unique. We would like to enforce
 * that constraint in the table. We cannot do so unfortunately as that will create a problem
 * when an attempt is made to add an account that was deleted previously. A delete operation
 * does not result in purging the row immediately. We only mark the deleted flag and set the
 * deleted_at timestamp. The actual purge will happen at a later point in time. This means the
 * row will linger around with the account name still there. Enforcing name uniqueness must be
 * handled by SQL functions that manipulate this table.
 */
create table if not exists main.accounts (
    id               uuid default gen_random_uuid() primary key,
    name             drioname not null check (length(name) >= 1),
    auth_type        drioaccountauthprovider not null default 'local',
    oauth_client_id  drioname,
    oauth_tenant_id  uuid, /* Only needed for Microsoft Entra ID */
    created_at       timestamptz not null default now(),
    updated_at       timestamptz not null default now(),
    deleted_at       timestamptz,
    deleted          boolean,
    country          driocountry not null check (length(country) > 1),
    state            drioname not null check (length(state) >= 1),
    city             drioname not null check (length(city) >= 1),
    schema_id        bigserial unique,
    schema_name      drioschema not null unique check (schema_name ~* concat('^', 'drio_account_', '[0-9]+$')),
    details          jsonb,
    constraint oauth_client_id_not_null
        check ((auth_type = 'local') or (oauth_client_id is not null)),
    constraint oauth_microsoft_tenant_id_not_null
        check ((auth_type <> 'microsoft') or (oauth_tenant_id is not null))
);

create trigger insert_account
before insert on main.accounts
for each row
execute procedure main.trigger_insert_account();

create trigger update_account
before update on main.accounts
for each row
execute procedure main.trigger_update_account();

create or replace function main.trigger_insert_admin() returns trigger as $insert_admin$
    begin
        new.deleted = false;
        return new;
    end;
$insert_admin$ language plpgsql;

create or replace function main.trigger_update_admin() returns trigger as $update_admin$
    begin
        new.created_at = old.created_at;
        new.updated_at = now();
        return new;
    end;
$update_admin$ language plpgsql;

/*
 * This table will hold the list of email addresses of users who are authorized to be
 * SaaS controller administrators. SaaS Administrator login supports OAuth and this means
 * anyone with a company email can login and become a SaaS Administrator. We don't want
 * this and this table allows us to prune the list. This should be ideally be taken care
 * of at our IDP (Microsoft Entra) but, that requires a license upgrade which we are not
 * planning for. This is a stop gap until the license change is in place.
 */
create table if not exists main.admins (
    email            drioemail primary key,
    created_at       timestamptz not null default now(),
    updated_at       timestamptz not null default now(),
    deleted_at       timestamptz,
    deleted          boolean
);

create trigger insert_admin
before insert on main.admins
for each row
execute procedure main.trigger_insert_admin();

create trigger update_admin
before update on main.admins
for each row
execute procedure main.trigger_update_admin();
