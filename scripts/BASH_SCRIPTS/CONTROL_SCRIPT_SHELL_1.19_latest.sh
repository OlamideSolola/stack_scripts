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
	# Variable declaration
	exp_backup_path=/backup/AWSSEP23/APEXDB	
	onprem_practicedir_path=/home/oracle/scripts/practicedir_ola_sep23	

	#checking to see if we have an APEXDB instance running
	
	database_instance=`ps -ef | grep pmon | grep APEXDB | awk '{print$8}'`

	if [[ $database_instance == ora_pmon_APEXDB ]]
	then
		echo "An APEXDB instance is up and running"
		
		#Running oracle database envinronment variable script to point to the right database
		. /home/oracle/scripts/oracle_env_APEXDB.sh
		
		#Logging into the database
		sqlplus stack_temp/stackinc@APEXDB<<EOF
		spool $onprem_practicedir_path/dbstatus.log
		show user
		select * from global_name;
		select status from v\$instance;
		spool off
EOF

		#checking if database is open
		if ( grep "OPEN" $onprem_practicedir_path/dbstatus.log )
		then 
			echo "Database is open, backup can commence"
		else
			echo "Database is not open"
		fi

		# Creating a for loop
		
		SCHEMAS=$each_schema

		for each_schema in $SCHEMAS		
		do

		#creating a parameter file
		
		echo "userid='/ as sysdba'" > expdp.par
		echo "schemas=${each_schema}" >> expdp.par
		echo "dumpfile=${each_schema}_${runner}_${TS}.dmp" >> expdp.par
		echo "logfile=${each_schema}_${runner}_${TS}.log" >> expdp.par
		echo "directory=${directory}" >> expdp.par
				
		
		#backing up the database
		expdp parfile=expdp.par
		
		#confirming the backup was successful
		grep "successfully completed" $exp_backup_path/${each_schema}_${runner}_${TS}.log
		
		#checking the exit status
		if (( $? != 0 ))
		then
			echo "Database backup was unsuccessful" | mailx -s "Unsuccesful database backup" stackcloud11@mkconsulting.net 
		else
			echo "Database backup successfully completed"
		fi	
	
	
		
		#changing directory to the /backup/AWSSEP23/APEXDB directory
		cd $exp_backup_path
		
		#Zipping up the dump file
		tar -cvf $exp_backup_path/${each_schema}_${runner}_${TS}.tar ${each_schema}_${runner}_*.dmp --remove-files
		
		#checking exist status
		if (( $? != 0 ))
		then
			echo "Dumpfile Zip failed"
		else
			echo " Dumpfile zip was successful"
		fi 
	
		
		#Data rentention 
		find $exp_backup_path -name "*Olamide*" -mtime +2 -exec rm -rf {} \;
		
		#Checking the exit status
		if (( $? != 0 ))
		then
			echo " Data retention failed"
		else
			echo "Data retention successful"
		fi

		# Changing directory to practicedir
		cd $onprem_practicedir_path
		done

	else
		echo "An APEXDB instance is not up and running"
	fi

}




database_migration()
{
	
	# Variable declaration
	imp_backup_path=/backup/datapump
	cloud_practicedir_path=/home/oracle/scripts/practicedir_ola_sep23

	# Creating a for loop
	SCHEMAS=$each_schema
	for each_schema in $SCHEMAS
	do

	# Calling the database backup function
	database_backup $each_schema $directory $runner
	

	# Checking the exit status of the export
	if (( $? !=0 ))
	then
		echo "Database schema export failed"
		exit
	else
		echo "The listed schema(s) was/were exported successfully" 
	fi 


	# Creating the import parameter file
	impdp_par_file=impdp_${each_schema}_stack_${runner}	

	echo "userid='/ as sysdba'" > $onprem_practicedir_path/$impdp_par_file.par
	echo "schemas=$each_schema" >> $onprem_practicedir_path/$impdp_par_file.par
	echo "remap_schema=$each_schema:stack_$runner_migrated" >> $onprem_practicedir_path/$impdp_par_file.par
	echo "dumpfile=${each_schema}_${runner}_${TS}.dmp" >> $onprem_practicedir_path/$impdp_par_file.par
	echo "logfile=$impdp_par_file.log" >> $onprem_practicedir_path/$impdp_par_file.par
	echo "directory=DATA_PUMP_DIR" >> $onprem_practicedir_path/$impdp_par_file.par
	echo "table_exists_action=replace" >> $onprem_practicedir_path/$impdp_par_file.par
	
	
	# Creating the import script
	echo "export ORACLE_HOME="/u01/app/oracle/product/12.1.0/db_1"" > import.sh
	echo "export ORACLE_SID=HERC" >> import.sh
	echo "/u01/app/oracle/product/12.1.0/db_1/bin/impdp parfile=$onprem_practicedir_path/$impdp_par_file.par" >> import.sh

	# Making the import script executable
	
	chmod 700 $onprem_practicedir_path/import.sh
	

	# SCPing the dumpfile, parameter file and the import file
	source_path="$onprem_practicedir_path/import.sh $onprem_practicedir_path/$impdp_par_file.par" 

	Secure_Copy $priv_key $source_path $dest_server $dest_dir

	# Checking the exit status
	if (( $? != 0 ))
	then
		echo "Par file and Import files were not copied"
	else
		echo "Parfile and Import file succesfully copied to the cloud" | mailx -s "Files successfully copied to the cloud" stackcloud11@mkconsulting.net
	fi

	# Copying tar file to backup directory
	source_path=${exp_backup_path}/${each_schema}_${runner}_${TS}.tar
	dest_dir=$imp_backup_path	

	Secure_Copy $priv_key $source_path $dest_server $dest_dir


	# Checking the exit status
	if (( $? != 0 ))
	then
		echo "Dumpfile was not copied"
	else
		echo "dumpfile succesfully copied to backup location" | mailx -s "Files successfully copied to the cloud" stackcloud11@mkconsulting.net
	fi
	
	# Untaring the zip file
	ssh -i ${priv_key} oracle@${dest_server} "tar -xvf $imp_backup_path/${each_schema}_${runner}_${TS}.tar -C $imp_backup_path" 
	
	# Checking exist status
	if (($? != 0 ))
	then
		echo "Untar failed"
		exit
	else
		echo " Tar ball successfully untarred"
	fi

	# Running the import
	dest_dir=$cloud_practicedir_path	
	ssh -i ${priv_key} oracle@${dest_server} $dest_dir/import.sh
	
	done	
	



}







#Main body


	#Checking the number of command line arguments entered
if [[ $# == 0 ]]
then
 
	#prompting the user for a function
	echo "You need to specify a function"
	echo "For file or directory backup, enter backup"
	echo "For the disk utilization, enter disk_utilization_check"
	echo "For database backup, enter database_backup"
	echo "For Secure Copy enter Secure_Copy"
	echo "For Database Migration enter database_migration"

	read -p "Entry : "  ENTERED

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
	#Checking if the entered function is database backup
	database_backup)

	#prompting user for necessary command line arguments
	
		read -p "Enter the schema or schemas to backup for multiple schemas, put the schemas in quotes. All schemas should be seperated by a space: " each_schema
		read -p "Specify the directory: " DIRECTORY
		read -p "Specify runner:" RUNNER
	
		schema=$each_schema
		directory=$DIRECTORY
		runner=$RUNNER
		TS=`date '+%m%d%y%H%M%S'`
	
		
		#Calling the database backup function
		database_backup $each_schema $directory $runner

	;;

		#checking if entered function is Secure Copy
		Secure_Copy)
	
		#prompting user for the necessary command line arguments

		read -p "Please specify destination server (onprem  or cloud ) : " SERVER_TYPE

		if [[ $SERVER_TYPE == cloud ]]
		then
			
		# prompting user for the right command line argument to scp to a cloud server

		read -p "Please Enter private key of the destination server : " priv_key
		read -p "Enter full path of source file or directory : " source_path
		read -p "Enter destination server: " dest_server
		read -p "Enter destination directory: " dest_dir

		# Calling the scp function

		Secure_Copy $priv_key $source_path $dest_server $dest_dir

		else [[ SERVER_TYPE == onprem ]]

			read -p " Enter full path of source file or directory : " source_path
			read -p " Enter destination server: " dest_server
			read -p " Enter destination directory: " dest_dir

		# Calling the scp function
		Secure_Copy $source_path $dest_server $dest_dir
		
		fi

	;;

		# Checking if entered function is Database Migration
	database_migration)

		# Prompting user for thr right input for a Database Migration
		read -p "Enter the location to create the parameter files: " SOURCE_PATH
		read -p "Enter schema or schemas to export. NB: Multiply schemas need to be in double quotes:  " EACH_SCHEMA
		read -p "Enter logical path/ database export directory: " DIRECTORY
		read -p "Enter runner name: " RUNNER
		read -p "Enter cloud server private key (full path): " PRIV_KEY
		read -p "Enter the import server hostname (cloud server): " DEST_SERVER
		read -p "Enter the location to scp the import parfile: " DEST_DIR

		each_schema=$EACH_SCHEMA
		directory=$DIRECTORY
		runner=$RUNNER
		priv_key=$PRIV_KEY
		source_path=$SOURCE_PATH
		dest_server=$DEST_SERVER
		dest_dir=$DEST_DIR
	
		# Calling the Database_Migration function
		database_migration $each_schema $directory $runner $priv_key $source_path $dest_server $dest_dir

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
	echo " Eg ./CONTROL_SCRIPT_SHELL_1.12.sh database_backup STACK_TEMP DATA_PUMP_DIR OLAMIDE"

elif [[ $1 == "database_backup" && $# == 4 ]]
	then 
	
	#Declaring the variables

	each_schema=$2	
	directory=$3
	runner=$4		
	TS=`date '+%m%d%y%H%M%S'`
	
		
	# Calling the database backup function
	database_backup $each_schema $directory $runner
	
	

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


	#Checking id function is data migration and we have wrong number of command line argument
elif [[ $1 == database_migration && $# != 7 ]]
then
	echo "USAGE: To perform a data migration, you need 1)Schemas to export 2)Directory 3)Runner 4)private key 5)destination server 6)destination dir"

	#Checking id function is data migration and we have the right  number of command line argument
elif [[ $1 == database_migration && $# == 7 ]]
then

	#Declaring the variables
	each_schema=$2
	directory=$3
	runner=$4
	priv_key=$5
	dest_server=$6
	dest_dir=$7
	TS=`date '+%m%d%y%H%M%S'`

	#Calling the database migration function

	database_migration $each_schema $directory $runner $priv_key $source_path $dest_server $dest_dir	


else
	echo "Function unknown"
fi

