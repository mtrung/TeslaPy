#!/bin/bash
file=~/.crontab
echo "30 10 * * * ~/dev/trung/TeslaPy/gsheet/gsheet.sh" > $file
# code -w $file
crontab $file
crontab -l

# code /var/mail/tvo