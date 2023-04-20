create database drio;

\connect drio

create schema accounts;

create table if not exists accounts.user (
    id int primary key,
    name varchar
);

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
