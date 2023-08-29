#!/bin/sh

cd /root
git clone https://github.com/drio-inc/client.git
cd /root/client
yarn install
./make-urls.sh $@
yarn build
yarn start
