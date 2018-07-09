#!/bin/bash

WORKING_DIR=$1
BACKUP_DIR=$2
VIRTUALENV_DIR=$3
DBBACKUP_FILE=backup-daily.sql.gz

cd $WORKING_DIR &&
. $VIRTUALENV_DIR/bin/activate &&
python manage.py dbbackup -z -O $BACKUP_DIR/$DBBACKUP_FILE
