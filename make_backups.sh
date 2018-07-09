#!/bin/bash

if [ -z $1 ] || [ -z $2 ] || [ -z $3 ] || [ $1 == "--help" ] || [ $1 == "-h" ]
then
    echo "Usage: $(basename $0) WORKING-DIR TARGET-DIR VIRTUALENV-DIR"
    echo ""
    echo "  WORKING-DIR       Directory where the backup command should be run"
    echo "  TARGET-DIR        Directory where the backup file should be stored"
    echo "  VIRTUALENV-DIR    Directory of virtualenv for the backup command; may be"
    echo "                    relative to WORKING-DIR"
    exit 1
fi

WORKING_DIR=$1
BACKUP_DIR=$2
VIRTUALENV_DIR=$3
DBBACKUP_FILE=backup.sql.gz

mkdir -p $BACKUP_DIR &&
cd $WORKING_DIR &&
. $VIRTUALENV_DIR/bin/activate &&
python manage.py dbbackup -z -O $BACKUP_DIR/$DBBACKUP_FILE
