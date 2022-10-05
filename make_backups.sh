#!/bin/bash

if [ -z $1 ] || [ -z $2 ] || [ -z $3 ] || [ -z $4 ] || [ -z $5 ] || [ $1 == "--help" ] || [ $1 == "-h" ]
then
    echo "Usage: $(basename $0) WORKING-DIR TARGET-DIR VIRTUALENV-DIR MEDIA_SOURCE_DIR MEDIA_BACKUP_DIR"
    echo ""
    echo "  WORKING-DIR       Directory where the backup command should be run"
    echo "  TARGET-DIR        Directory where the backup file should be stored"
    echo "  VIRTUALENV-DIR    Directory of virtualenv for the backup command; may be relative to WORKING-DIR"
    echo "  MEDIA_SOURCE_DIR  Directory containing the media files to be backed up; may be relative to WORKING-DIR"
    echo "  MEDIA_BACKUP_DIR  Directory for backing up media files; may be relative to WORKING-DIR"
    exit 1
fi

WORKING_DIR=$1
BACKUP_MAIN_DIR=$2
VIRTUALENV_DIR=$3
MEDIA_SOURCE_DIR=$4
MEDIA_BACKUP_DIR=$5

FILENAME_PREFIX=$(date +%Y-%m-%d_%H.%M.%S)

mkdir -p $BACKUP_MAIN_DIR/logs
BACKUP_LOG=$BACKUP_MAIN_DIR/logs/backup_${FILENAME_PREFIX}.log

# Determine the type of backup: quarterly, monthly, weekly or daily
DAYOFMONTH=$(date +%d)
if [ $DAYOFMONTH == 01 ]; then
    MONTH=$(date +%m)
    if [ $MONTH == 01 ] || [ $MONTH == 04 ] || [ $MONTH == 07 ] || [ $MONTH == 10 ]; then
        # Quarterly. KEEP!!
        BACKUP_SUBDIR=quaterly
        MAX_NUMBER_OF_FILES=-1;
    else
        BACKUP_SUBDIR=monthly;
        MAX_NUMBER_OF_FILES=8;
    fi
else
    DAYOFWEEK=$(date +%w)
    if [ $DAYOFWEEK == 0 ]; then
        BACKUP_SUBDIR=weekly;
        MAX_NUMBER_OF_FILES=5;
    else
        BACKUP_SUBDIR=daily;
        MAX_NUMBER_OF_FILES=6;
    fi
fi

# Create the backup directory if it doesn't exist
BACKUP_DIR=$BACKUP_MAIN_DIR/$BACKUP_SUBDIR
mkdir -p $BACKUP_DIR

# Delete the oldest backups if the number of backups exceed the max
echo -e "\n--- Deleting obsolete database backups ---" | tee -a $BACKUP_LOG
if [ $MAX_NUMBER_OF_FILES -gt 0 ]; then
    ls -A1t $BACKUP_DIR | tail -n +$MAX_NUMBER_OF_FILES | tee -a /dev/fd/2 $BACKUP_LOG | xargs -i --no-run-if-empty rm $BACKUP_DIR/{};
fi

DBBACKUP_FILE=${FILENAME_PREFIX}_backup.sql

# Backup database
echo -e "\n--- Backing up the database ---" | tee -a $BACKUP_LOG
cd $WORKING_DIR &&
. $VIRTUALENV_DIR/bin/activate &&

DB_PASSWORD=$(grep DB_PASSWORD .env | perl -pe 's/.*?=//')
mysqldump mediatedb_test --quick --host=mysql-mediatedb.science.ru.nl --user=mediatedb_admin --password=$DB_PASSWORD --no-tablespaces > $BACKUP_DIR/$DBBACKUP_FILE 2> >(tee -a $BACKUP_LOG)
gzip $BACKUP_DIR/$DBBACKUP_FILE

# Backup media file
echo -e "\n--- Backing up media files ---" | tee -a $BACKUP_LOG
rsync -av $MEDIA_SOURCE_DIR $MEDIA_BACKUP_DIR | tee -a $BACKUP_LOG
