#!/bin/bash


#variable declaration
source=/home/oracle/scripts/practicedir_ola_sep23/backup/file3.txt_120923175525
destination=/home/oracle/scripts/practicedir_ola_sep23/backup/file3.txt
TS=`date '+%m%d%y%H%M%S'`
destination=${destination}"_"${TS}


#Main body

#copying a file to the backup directory
echo "copying file ${source} to ${destination}"
cp -r ${source} ${destination}
echo "file ${source} has been successfully copied to ${destination}"



