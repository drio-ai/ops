\connect drio

drop table if exists accounts.user;
drop table if exists accounts.ou;
drop schema accounts;

drop table if exists config.datasource;
drop table if exists config.ddx;
drop schema config;

\connect postgres
drop database drio;
