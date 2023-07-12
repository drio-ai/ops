#!/bin/sh

cwd=$(pwd)
prefix=${cwd}/vault/compose
[ ! -d ${prefix} ] && echo "Did not find directory ${prefix}" && exit 1
mkdir -p ${prefix}/config ${prefix}/policies ${prefix}/data ${prefix}/logs ${prefix}/tokens/root ${prefix}/tokens/drio-controller
