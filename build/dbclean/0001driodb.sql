\connect drio

drop table if not exists accounts.user (
    id int primary key,
    name varchar
);

drop table if not exists accounts.ou (
    id int primary key,
    name varchar
);

drop schema accounts;

drop table if not exists config.datasource (
    id int primary key,
    name varchar
);

drop table if not exists config.ddx (
    id int primary key,
    name varchar
);

drop schema config;

drop database drio;
