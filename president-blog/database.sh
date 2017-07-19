#!/bin/bash
service postgresql start
su -c 'psql -c "create database task200" && psql task200 < file.sql' postgres
service postfix start
service apache2 start
tail -f /var/log/apache2/access.log