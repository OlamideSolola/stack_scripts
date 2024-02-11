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

	#checking use%

		use=`df -h|grep $disk| awk '{print $4}'|sed 's/%//g'`	 	
		echo "The current use% is $use"

	if [[  $use > $threshold ]]
	then
		echo "Disk utilization is above Threshold!"
	fi 
}




#Main body

function=$1

   #Checking the number of command line arguments entered for the backup function
if [[ $function == "backup" && $# != 4 ]]
then
	#Stating how to use the script for a backup function
	echo "USAGE: In order to do a backup using this script, you need to: "	
	echo " 1) Enter the source"
	echo " 2) Enter the destination"
	echo " 3) Specify Runner"
	echo "Eg ./CONTROL_SCRIPT_SHELL_1.9.sh source destination runner"
	exit

elif [[ $function == "backup" && $# == 4 ]]
then
	echo "The backup function has been selected" 
	source=$2
	destination=$3
	runner=$4
	TS=`date '+%m%d%y%H%M%S'`
	destination=${destination}/${runner}/${TS}

	# calling the backup function
	backup_f_d $source $destination $runner

	#Checking the number of command line arguments entered for the disk utilization function
elif [[ $function == "disk_utilization_check" && $# != 3 ]]
then
	echo "USAGE: To check the Disk utilization using this script, you need to: "
	echo " 1) Enter the Threshold"
	echo " 2) Enter the Disk you want to check"
	echo "Eg ./CONTROL_SCRIPT_SHELL_1.9.sh Threshold Disk"
	exit

elif [[ $function == "disk_utilization_check" && $# == 3 ]]
then
	threshold=$2
	disk=$3

	# calling the disk utilization function
	disk_utilization_check $threshold $disk
else
	echo "Function unknown"
fi






