# Backup Configuration

## Daily Backup

Database backup at 2 AM
File backup at 3 AM

## Cron

0 2 * * * /scripts/backup_db.sh
0 3 * * * /scripts/backup_files.sh
