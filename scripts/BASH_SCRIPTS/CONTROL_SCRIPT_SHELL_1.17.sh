#!/bin/bash
#functions
Secure_Copy ()
{	
	#Declartion of variables
	cloud=`grep $dest_server /home/oracle/scripts/practicedir_ola_sep23/cloud_servers.txt`
	onprem=`grep $dest_server /home/oracle/scripts/practicedir_ola_sep23/onprem_servers.txt`

	#Checking if the destination server is an onprem server
	
	if [[ $dest_server == $onprem ]]
	then
		echo "Copying $source_path from the cloud server to onprem server"

	#Pushing files or directories from the cloud server to the onprem server
	scp -r $source_path oracle@$dest_server:$dest_dir
		

	#Checking the exit status
	
		if (( $? != 0 ))
		then
			echo "Secure Copy from the cloud to the onprem server failed"
		else
			echo "$source_path was successfully copied to $dest_server "
		fi

	#checking if the destination server is a cloud server

	elif [[ $dest_server == $cloud ]]
	then	
		echo "Copying $source_path from the onprem server to the cloud server"

	#Pushing files or directories from the onprem server to the cloud server
	scp -r -i $priv_key $source_path oracle@$dest_server:$dest_dir
	
	
	#Checking the exit status 
		if (( $? != 0 ))
		then
			echo "Secure Copy from onprem to the cloud failed"
		else
			echo "$source_path was succesfully copied to $dest_server"
		fi

	else
		echo "server not know"
	fi

}


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
	else
		echo " "
	fi 
}



database_backup()
{
	
	#checking to see if we have an APEXDB instance running
	
	database_instance=`ps -ef | grep pmon | grep APEXDB | awk '{print$8}'`

	if [[ $database_instance == ora_pmon_APEXDB ]]
	then
		echo "An APEXDB instance is up and running"

		#Running oracle database envinronment variable script to point to the right database
		. /home/oracle/scripts/oracle_env_APEXDB.sh
		
		#Logging into the database
		sqlplus stack_temp/stackinc@APEXDB<<EOF
		spool /home/oracle/scripts/practicedir_ola_sep23/dbstatus_1.12.log
		show user
		select * from global_name;
		select status from v\$instance;
		spool off
EOF

		#checking if database is open
		if ( grep "OPEN" /home/oracle/scripts/practicedir_ola_sep23/dbstatus_1.12.log )
		then 
			echo "Database is open, backup can commence"
		else
			echo "Database is not open"
		fi
		
		#creating a parameter file
		
		echo "userid='/ as sysdba'" > expdp.par
		echo "schemas=${schema}" >> expdp.par
		echo "dumpfile=${dumpfile}" >> expdp.par
		echo "logfile=${logfile}" >> expdp.par
		echo "directory=${directory}" >> expdp.par
				
		
		#backing up the database
		expdp parfile=expdp.par
		
		#confirming the backup was successful
		grep "successfully completed" /backup/AWSSEP23/APEXDB/${logfile}
		
		#checking the exit status
		if (( $? != 0 ))
		then
			echo "Database backup was unsuccessful" | mailx -s "Unsuccesful database backup" stackcloud11@mkconsulting.net 
		else
			echo "Database backup successfully completed"
		fi	


		#Zipping up the dump file		
		tar -cvf /backup/AWSSEP23/APEXDB/${schema}_${runner}_${TS}.tar /backup/AWSSEP23/APEXDB/${schema}_${runner}*.dmp --remove-files		

		#checking exist status
		if (( $? != 0 ))
		then
			echo "Zip failed"
		else
			echo " Dumpfile zip was successfully"
		fi 
		
		#Data rentention 
		find /backup/AWSSEP23/APEXDB -name "*Olamide*" -mtime +2 -exec rm -rf {} \;
		
		#Checking the exit status
		if (( $? != 0 ))
		then
			echo " Data retention failed"
		else
			echo "Data retention successful"
		fi

	else
		echo "An APEXDB instance is not up and running"
	fi
}










#Main body


	#Checking the number of command line arguments entered
if [[ $# == 0 ]]
then
 
	#prompting the user for a function
	echo "You need to specify a function"
	echo "For the backup function, enter backup:"
	echo "For the disk utilization function, enter disk_utilization_check"
	echo "For database backup, enter database_backup"
	echo "For Secure Copy enter Secure_Copy"
	echo "Zip enter zip"
	read -p "Entry :"  ENTERED

	case $ENTERED in

	#Checking if the entered function is backup
	backup)

	#Prompting the user for the necessary command line arguments for a backup
		read -p "Specify the source: " SOURCE_ENTERED
		read -p "Specify the destination: " DESTINATION_ENTERED
		read -p "Specify the runner: " RUNNER_ENTERED

	#Declaring the variables
		source=$SOURCE_ENTERED
		destination=$DESTINATION_ENTERED
		runner=$RUNNER_ENTERED
		TS=`date '+%m%d%y%H%M%S'`
		destination=${destination}/${runner}/${TS}

	#Calling the backup function
	backup_f_d $source $destination $runner
	
	#Checking the exit status and Sending a mail for both succesful and unsuccesful backup 
		if (( $? != 0 ))
		then
			echo "The Backup failed" | mailx -s "Backup failed" stackcloud11@mkitconsulting.net 
		else
			echo "The backup was successfull" | mailx -s "Successful backup" stackcloud11@mkitconsulting.net
 		fi
	
	;;

	#checking if the entered function is disk utilization
	disk_utilization_check)

	#prompting the user for the necessary command line arguments
		read -p "Specify the Threshold: " THRESHOLD_ENTERED
		read -p "Specify the disk: " DISk_ENTERED
		
		threshold=$THRESHOLD_ENTERED
		disk=$DISk_ENTERED

	#calling the disk utilization function
	disk_utilization_check $threshold $disk
	
	#Checking the exit status and Sending a mail
		if (( $? != 0 ))
		then
			echo "Disk utilization check failed" | mailx -s "Disk utilization check failure" stackcloud11@mkconsulting.net
		else
			echo "Disk utilization check was successful" | mailx -s "Disk utilization check sucessful" stackcloud11@mkconsulting.net
		fi
	
	;;

	*)
		echo "Function not know"
	;;
	esac

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
	
	#Calling the backup function
	backup_f_d $source $destination $runner


	#Checking the exit status and sending a mail
	if (( $? != 0 ))
	then
		echo "Backup failed" | mailx -s "Backup failed" stackcloud11@mkconsulting.net
	else
		echo "Backup sucessful" | mailx -s "Backup sucessful" stackcloud11@mkconsulting.net
	fi

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
	
	# Calling the disk utilization function 
	disk_utilization_check $threshold $disk
	
	#checking the exit status and sending a mail
	if (( $? != 0 ))
	then
		echo "Disk utilization check failed!" | mailx -s "Disk utilization check failure" stackcloud11@mkconsulting.net
	else
		echo "Disk utilization check was sucessfull" | mailx -s "Disk utilization check sucessful" stackcloud11@mkconsulting.net
	fi

elif [[ $1 == "database_backup" && $# != 4 ]]
then
	#Stating how to use the script for a backup
	echo "USAGE: To do a database backup you need: "
	echo "1)Schema you want to backup 2)Directory 3)Runner"
	echo " Eg ./CONTROL_SCRIPT_SHELL_1.12.sh database_backup expdp_1.12.par STACK_TEMP DATA_PUMP_DIR OLAMIDE"

elif [[ $1 == "database_backup" && $# == 4 ]]
	then 
	#Declaring the variables
	schema=$2
	directory=$3
	runner=$4		
	TS=`date '+%m%d%y%H%M%S'`
	dumpfile=${schema}_${runner}_${TS}.dmp
	logfile=${schema}_${runner}_${TS}.log

	# Calling the database backup function
	database_backup $schema $directory $runner	
	
	# Checking if the function called is secure copy
elif [[ $1 == Secure_Copy ]]
then
	
	# Checking if the command line arguments entered is equal to 5
       if [[ $# == 5 ]]
		then

	# Declaring Variables
	priv_key=$2				
	source_path=$3
	dest_server=$4
	dest_dir=$5

	# Calling the secure copy function
	Secure_Copy $priv_key $source_path $dest_server $dest_dir
		
	# Checking the exist status
			if (( $? != 0 ))
			then
				echo " Secure copy failed"
			else 
				echo " "
			fi

		elif [[ $# == 4 ]]
		then	
	# Declaring variables
	source_path=$2
	dest_server=$3
	dest_dir=$4
	
	# Calling the secure copy function
	Secure_Copy $source_path $dest_server $dest_dir
	
	# Checking the exit status
			if (( $? != 0 ))
			then
				echo "Secure Copy failed"
			else
				echo " "
			fi	
		
		else
			echo "USAGE: To copy files or directories between servers you need: "
			echo "1)The source path 2) The destination server 3)The destination path"
			echo " Eg./CONTROL_SCRIPT_SHELL_1.14.sh Secure_Copy  Source path Destination server Destination path"
			echo "If the destination server is a cloud server, then you will need a private key as well"
			echo "EG ./CONTROL_SCRIPT_SHELL_1.14.sh Secure_Copy Private Key Source path Destination server Destination path"
			fi


elif [[ $1 == zip && $# == 4 ]]
then
	# Declaring variables
	name=$2
	runner=$3
	files_to_zip=$4
	zip_file_name=$name_$runner_$TS.tar
	TS=`date '+%m%d%y%H%M%S'`

	# Calling the zip function
	zip ${zip_file_name}${runner} ${files_to_zip}


elif [[ $1 == zip && $# != 4 ]]
then
   echo "USAGE:To zip up files, please enter the following information: "
	echo " 1)Zip file name 2)Runner 3) The files to zip"
	echo "EG ./CONTROL_SCRIPT_SHELL_1.16.sh stack_temp olamide *stack_temp.dmp "

else
	echo "Function unknown"
fi

