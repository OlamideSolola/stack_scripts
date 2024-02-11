#!/bin/bash


#variable declaration
source=/home/oracle/scripts/practicedir_ola_sep23/backup/text.txt
destination=/home/oracle/scripts/practicedir_ola_sep23/backup
TS=`date '+%m%d%y%H%M%S'`
Runner=ABI
source=${source}
destination=${destination}/${Runner}/${TS}


#Main body

#Creating a directory
mkdir -p ${destination}

#copying a file to the backup directory
echo "copying file ${source} to ${destination}"
cp -r ${source} ${destination}
echo "file ${source} has been successfully copied to ${destination}"



