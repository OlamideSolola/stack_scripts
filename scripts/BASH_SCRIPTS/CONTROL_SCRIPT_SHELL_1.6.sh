#!/bin/bash

#functions
backup_f_d ()
{
	echo "copying file ${source} to ${destination}"

	#Creating a directory
	mkdir -p ${destination}

	#checking exit status
	if (( $? !=0 ))
	then
		echo "A directory was not created"
	fi

	#copying file to back up directory
	cp -r ${source} ${destination}

	#checking exit status 
	if (( $? !=0 ))
	then
		echo "copy command failed"
	else
		echo "file ${source} has been successfully copied to ${destination}"
	fi

}


disk_utilization_check ()
{
	df -h 
}


#Main body

function=$1

if [[ $function == "backup" ]]
then
	echo "The backup function has been selected" 
	source=$2
	destination=$3
	runner=$4
	TS=`date '+%m%d%y%H%M%S'`
	destination=${destination}/${runner}/${TS}

	# calling the backup function
	backup_f_d $source $destination $runner

elif [[ $function == "disk_utilization_check" ]]
then
	Threshold=$2

	# calling the disk utilization function
	disk_utilization_check $Threshold
else
	echo "Function unknown"
fi
