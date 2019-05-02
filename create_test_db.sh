#!/usr/bin/env bash
# This script dumps the schema and Django data of the main
# MySQL database and puts it in a test MySQL database.
#
# It is assumed that the test database is already created
# and that both databases have the same credentials.
#
# Running Django tests:
#     pip install django-test-without-migrations
#     pip install django-nose
#     ./manage.py test --keepdb --nomigrations --setting=mediate.settings_tests

# Settings
TMPDIR=/tmp
MYSQLUSER=mediate_admin
MAINDB=mediate
TESTDB=test_mediate

# Get a datetime stamp
DATETIMESTAMP=$(date +%Y-%m-%d_%H.%M.%S)

# File name of the MySQL dump
SQLFILE=$TMPDIR/${MAINDB}_$DATETIMESTAMP.sql

# Prompt the MySQL password
echo -n "MySQL password: "
read -s PASSWORD
echo # Creates a newline in the output

# Dump the schema
echo -n "Dumping the schema... "
mysqldump -u $MYSQLUSER -p$PASSWORD --no-data $MAINDB > $SQLFILE 2> >(grep -v "\[Warning\] Using a password")
echo "Done."

# Dump data for the standard Django tables (ignoring the Mediate data tables)
# and append to the same file as the schema
echo -n "Dumping the Django data... "
mysqldump -u $MYSQLUSER -p$PASSWORD --no-create-info $MAINDB auth_group auth_group_permissions auth_permission \
auth_user auth_user_groups auth_user_user_permissions django_admin_log django_content_type django_migrations \
django_session django_site frontend_module >> $SQLFILE 2> >(grep -v "\[Warning\] Using a password")
echo "Done."

# Import it into the test database
echo -n "Importing in the test database... "
mysql -u $MYSQLUSER -p$PASSWORD $TESTDB < $SQLFILE 2> >(grep -v "\[Warning\] Using a password")
echo "Done."

# Clean up
rm $SQLFILE