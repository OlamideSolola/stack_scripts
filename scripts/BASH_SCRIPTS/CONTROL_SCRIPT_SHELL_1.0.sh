#!/bin/bash

#variable declaration
source=/home/oracle/scripts/practicedir_ola_sep23/test1.0.txt
destination=/home/oracle/scripts/practicedir_ola_sep23/backup


#Main body

#copying a file to the backup directory
echo "copying file ${source} to ${destination}"
cp ${source} ${destination}
echo "file ${source} has been successfully copied to ${destination}"



