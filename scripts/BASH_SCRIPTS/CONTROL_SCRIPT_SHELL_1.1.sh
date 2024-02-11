#!/bin/bash


#variable declaration
source=/home/oracle/scripts/practicedir_ola_sep23/test1.1.txt
destination=/home/oracle/scripts/practicedir_ola_sep23/backup/test1.1.txt
TS=`date '+%m%d%y%H%M%S'`
destination=${destination}"_"${TS}


#Main body

#copying a file to the backup directory
echo "copying file ${source} to ${destination}"
cp ${source} ${destination}
echo "file ${source} has been successfully copied to ${destination}"



