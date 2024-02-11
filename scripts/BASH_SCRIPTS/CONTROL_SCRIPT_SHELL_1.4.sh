#!/bin/bash


#variable declaration
source=$1
destination=$2
Runner=$3
TS=`date '+%m%d%y%H%M%S'`
destination=${destination}/${Runner}/${TS}/


#Main body

#Creating a directory
mkdir -p ${destination}

#copying a file to the backup directory
echo "copying file ${source} to ${destination}"
cp -r ${source} ${destination}
echo "file ${source} has been successfully copied to ${destination}"



