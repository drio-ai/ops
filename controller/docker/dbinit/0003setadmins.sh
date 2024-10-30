#!/bin/sh

if [[ ! -z ${DRIO_SAAS_ADMINS} ]]; then
    DRIO_DEFAULT_SAAS_ADMINS="${DRIO_DEFAULT_SAAS_ADMINS},${DRIO_SAAS_ADMINS}"
fi

# Split on comma
IFS=','
for admin in ${DRIO_DEFAULT_SAAS_ADMINS}; do
    # Remove leading and trailing spaces if any
    admin=$(echo ${admin} | xargs)
    if [[ ! -z ${admin} ]]; then
        psql --dbname=drio --command "INSERT INTO main.admins(email) VALUES('${admin}');"
    fi
done
