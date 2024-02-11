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



database_backup()
{

	#confirming we are on the right server for the backup
	hostname=MKIT-DEV-OEM

	if [[ $hostname == "MKIT-DEV-OEM" ]]
	then
		echo "We are on the right server for this backup"
	fi	
	

		#Running oracle database envinronment variable script to point to the right database
		. /home/oracle/scripts/oracle_env_APEXDB.sh
		
		#Logging into the database
		sqlplus stack_temp/stackinc@APEXDB<<EOF
		spool /home/oracle/scripts/practicedir_ola_sep23/dbstatus_1.11.log
		show user
		select * from global_name;
		select status from v\$instance;
		spool off
EOF

		#checking if database is open
		if ( grep "OPEN" /home/oracle/scripts/practicedir_ola_sep23/dbstatus_1.11.log )
		then 
			echo "Database is open, backup can commence"
		else
			echo "Database is not open"
		fi

		#backing up the database
		expdp parfile=expdp_stack_temp_1.11.par
		

	

}



#Main body


	#Checking the number of command line arguments entered
if [[ $# == 0 ]]
then
 
	#prompting the user for a function
	echo	  "You need to specify a function"
	echo	  "For the backup function, enter backup:"
	echo	  "For the disk utilization function, enter disk_utilization_check"
	read -p "Entry :"  ENTERED

	#Checking if the entered function is backup
	if [[ $ENTERED == "backup" ]]
	then 

	#Prompting the user for the necessary command line arguments for a backup
		read -p "Specify the source: " SOURCE_ENTERED
		read -p "Specify the destination: " DESTINATION_ENTERED
		read -p "Specify the runner: " RUNNER_ENTERED

		source=$SOURCE_ENTERED
		destination=$DESTINATION_ENTERED
		runner=$RUNNER_ENTERED
		TS=`date '+%m%d%y%H%M%S'`
		destination=${destination}/${runner}/${TS}

	#Calling the backup function
	backup_f_d $source $destination $runner

	#checking if the entered function is disk utilization
	elif [[ $ENTERED == "disk_utilization_check" ]]
		then

	#prompting the user for the necessary command line arguments
		read -p "Specify the Threshold: " THRESHOLD_ENTERED
		read -p "Specify the disk: " DISk_ENTERED
		
		threshold=$THRESHOLD_ENTERED
		disk=$DISk_ENTERED

	#calling the disk utilization function
	disk_utilization_check $threshold $disk
	fi

	#checking if the function specified by the user is backup and they have the right number of command line argument
elif [[ $1 == "backup" && $# != 4 ]]
	then

   #Stating how to use the script for a backup function
   	echo "USAGE: In order to do a backup using this script, you need to:"
		echo "1) Enter the source"
		echo "2) Enter the destination"
		echo "3) Enter the runner"
		echo "Eg ./CONTROL_SCRIPT_SHELL_1.10.sh source destination runner"
		exit	

	#checking if the function specified by the user is backup and they have the right number of command line argument 
elif [[ $1 == "backup" && $# == 4 ]]
	then
		echo  "The backup function has been selected"
		source=$2
		destination=$3
		runner=$4
		TS=`date '+%m%d%y%H%M%S'`
		destination=${destination}/${runner}/${TS}
	
	# calling the backup function
	backup_f_d $source $destination $runner

	#checking if the function specified by the user is disk utilization and they have the right number of command line arguments 
elif [[ $1 == "disk_utilization_check" && $# != 3 ]] 
	then

	# stating how to use the script for a disk utilization check
		echo "USAGE: To check the disk utilization using this script, you need to: "
		echo "1) Enter the Threshold"
		echo "2) Enter the Disk you want to check"
		echo "Eg ./CONTROL_SCRIPT_SHELL_1.10.sh Threshold Disk"

	#checking if the function entered by the user is disk utlization and they have the right number of command line argument
elif [[ $1 == "disk_utilization_check" && $# == 3 ]]
	then
		threshold=42
		disk=$3
	
	# calling the disk utilization function 
	disk_utilization_check $threshold $disk

elif [[ $1 == "database_backup" ]]
	then
	# calling the database backup function
	database_backup	

else
	echo "Function unknown"

fi

