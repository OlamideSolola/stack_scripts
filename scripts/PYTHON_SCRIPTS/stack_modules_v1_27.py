#!/usr/bin/bash

# Import Modules
import time,os,shutil,sys,gzip,smtplib,subprocess,datetime
import cx_Oracle as c
import boto3,botocore
from botocore.exceptions import ClientError
import personals as p


# Variable declaration
timestring=time.localtime()
TS=time.strftime("%m%d%Y%H%M%S", timestring)


# Function definition

def db_connection(**args):
 
	# Declaring variables
	status = ["Running","Completed", "Error"]
	status_before_job_run, status_after_job_run, status_job_error = status
	
	# Connecting into the database with our connection details
	connection=c.connect(user="STACK_OLA_SEP23", password=p.db_password, dsn=p.APEXDB_dsn)

	# Defining the cursor
	cursor=connection.cursor()

	# Checking if the job status is running
	if args["args15"] == status_before_job_run:
		print("Job run started, inserting job info into the database")
 		
		# Reading the PROD_OPERATIONS table for Operation ID
		cursor.execute("""select OP_ID from PROD_OPERATIONS where OP_NAME = :OP_NAME_INS""",
		OP_NAME_INS=args['args11'])

		print("The Operation name is {}".format(args['args11']))

		# Getting the result of our above select statement
		read_OP_ID = cursor.fetchone()
		
		# Extracting the OP_ID from the tuple
		OP_ID_TO_USE=read_OP_ID[0]
		print("Read OP ID is " + str(OP_ID_TO_USE))

		
		# Reading the PROD_OPERATIONS table for Monitoring email
		cursor.execute("""select MONITORING_EMAIL from PROD_OPERATIONS where OP_NAME= :OP_NAME_INS""",
		OP_NAME_INS=args['args11'])
		
		# Getting the result of our above select statement
		read_MON_EMAIL = cursor.fetchone()

		# Extracting the email from the tuple
		MON_EMAIL_TO_USE = read_MON_EMAIL[0]
		print("Read Monitoring Email is " + str(MON_EMAIL_TO_USE))

		# Inserting data into the rows
		cursor.execute("""insert into PROD_ACTIVITIES values(:OP_ID_INS,:OP_STARTTIME_INS,:OP_ENDTIME_INS,:RUNNER_INS,:STATUS_INS, :MON_EMAIL_INS)""",
		OP_ID_INS=OP_ID_TO_USE,
		OP_ENDTIME_INS=args['args17'],
		OP_STARTTIME_INS=args['args12'],
		RUNNER_INS=args['args14'],
		STATUS_INS=args['args15'],
		MON_EMAIL_INS=MON_EMAIL_TO_USE)
	
		# Commiting the updates made
		connection.commit()
		
	# Checking if the job status is completed
	elif args["args15"] == status_after_job_run:
		print("Job completed, updating the operations table with end time and new status")	
	
		# Reading the PROD_OPERATIONS table for Operation ID
		cursor.execute("""select OP_ID from PROD_OPERATIONS where OP_NAME = :OP_NAME_INS""",
		OP_NAME_INS=args['args11'])

		# Getting the result of our above select statement
		read_OP_ID = cursor.fetchone()

		# Extracting the OP_ID from the tuple
		OP_ID_TO_USE=read_OP_ID[0]	
		print("Read OP ID is " + str(OP_ID_TO_USE))
	
		# Updating the created row with endtime information
		cursor.execute("""update PROD_ACTIVITIES set OP_ENDTIME = :OP_ENDTIME_INS, STATUS = :STATUS_INS where RUNNER = :RUNNER_INS and OP_STARTTIME = :OP_STARTTIME_INS and OP_ID = :OP_ID_TO_USE""",
		OP_ENDTIME_INS=args['args17'],
		STATUS_INS=args['args15'],
		RUNNER_INS=args['args14'],
		OP_STARTTIME_INS=args['args12'],
		OP_ID_TO_USE = read_OP_ID[0])
		
		# Commiting the updates made
		connection.commit()

		print("Job Endtime and status updated")	
		
		
		# Doing a Join between the activities and the prod operations tables
		# Aliasing prod_operations as a and prod_activities as b
		cursor.execute("""select a.OP_ID,a.OP_NAME,b.OP_STARTTIME,b.OP_ENDTIME,b.RUNNER,b.STATUS,b.MON_EMAIL from PROD_OPERATIONS a right JOIN PROD_Activities b on a.OP_ID = b.OP_ID where OP_STARTTIME = :OP_STARTTIME_INS""",
		OP_STARTTIME_INS=args['args12'])
		joined_table_info= cursor.fetchone()
		print("Right Join completed")
	
	
		# Printing the operation information
		print("Information regarding the completed operation:")
		OP_NAME = joined_table_info[1]
		OP_ID = joined_table_info[0]
		OP_STARTTIME = joined_table_info[2]	
		OP_ENDTIME = joined_table_info[3]
		OP_RUNNER = joined_table_info[4]
		OP_STATUS = joined_table_info[5]
		MONITORING_EMAIL = joined_table_info[6]

		print("OP_NAME = {}\nOP_ID = {}\nOP_STARTTIME = {}\nOP_ENDTIME = {}\nOP_RUNNER = {}\nOP_STATUS = {}\nMONITORING_EMAIL = {}" .format(OP_NAME,OP_ID,OP_STARTTIME,OP_ENDTIME,OP_RUNNER,OP_STATUS,MONITORING_EMAIL))
		
	# Checking if the job status is "error"
	elif args["args15"] == status_job_error:
		print("Job not completed, updating the operations table with an error status")

		# Updating the created row with endtime information
		cursor.execute("""update PROD_ACTIVITIES set OP_ENDTIME = :OP_ENDTIME_INS, STATUS = :STATUS_INS where RUNNER = :RUNNER_INS""",
		OP_ENDTIME_INS=args['args17'],
		STATUS_INS=args['args15'],
		RUNNER_INS=args['args14'])

		# Commiting the updates made
		connection.commit()


def STACK_EMAIL(TO_EMAIL, SUBJECT, BODY, FROM):
	
	try:
		# Variable declaration
		FROM="oracle@MKIT-DEV-OEM.localdomain"

		MSG=("\n".join(("FROM: %s" %FROM, "To: %s" %TO_EMAIL, "Subject: %s:\n" %SUBJECT, "%s" %BODY)))

		with smtplib.SMTP('localhost') as my_server:
			my_server.sendmail(FROM, TO_EMAIL, MSG)
			print("Email sent successfully to %s" %TO_EMAIL)

	except:
		print("Email not sent")


def database_backup(**args):

	# Variable Declaration
	runner = args["args2"]
	user="'/ as sysdba'"
	dumpfile=args["args1"] + "_" + args["args2"] + "_" + TS + ".dmp"
	logfile=args["args1"] + "_" + args["args2"] + "_" + TS + ".log"
	base_path="/home/oracle/scripts/practicedir_ola_sep23/"
	par_file_name="export_" + args["args1"] + "_" + TS + ".par"
	par_file_fullpath=os.path.join(base_path, par_file_name)
	exp_pysical_path="/backup/AWSSEP23/APEXDB/"
	full_exp_physical_path=os.path.join(exp_pysical_path, runner, TS)
	export_command_file="export.sh"
	export_command_file_fullpath=os.path.join(base_path, export_command_file)
	dumpfile_fullpath=os.path.join(base_path,dumpfile)
	logfile_fullpath=os.path.join(base_path,logfile)
	status = ["Running","Completed", "Error"]
	status_before_job_run, status_after_job_run, status_job_error = status
	STATUS_INS = status_before_job_run
	current_datetime=datetime.datetime.now()
	current_datetime_formated=current_datetime.strftime("%d-%b-%y %I:%M:%S %p")
	OP_NAME_INS = args['args11']
	OP_STARTTIME_INS= current_datetime_formated
	OP_ENDTIME_INS = current_datetime_formated
	RUNNER_INS = runner
	OP_TYPE_INS = args['args16']


	print(par_file_fullpath)
	
	# Calling the db connection function to log start of the database backup activity
	db_connection(args15=STATUS_INS, args11=OP_NAME_INS, args12=OP_STARTTIME_INS, args14= RUNNER_INS, args16=OP_TYPE_INS, args17=OP_ENDTIME_INS)
	
	try:
		# Creating a parameter file in write and read mode
		fo=open(par_file_fullpath, "w+")
	
		# Writing into the parameter file
		fo.write("userid=" + user + "\nschemas=" + args["args1"] + "\ndumpfile=" + dumpfile + "\nlogfile=" + logfile + "\ndirectory=" + args["args3"])
	
		# Closing the parameter file
		fo.close()

		# Opening the parameter file in read + mode
		fo=open(par_file_fullpath, "r+")

		# Assigning the content of the parameter file to a variable
		file_content=fo.read()
	
		# Printing the content of the parameter file to standard output
		print(file_content)

		# Closing the parameter file
		fo.close()	
	
		# Confirming that the par file was created
		if par_file_fullpath:
			print("Parameter file was successfully created")

	
		# Setting the oracle env variable and writing the export command
		exp=open(export_command_file_fullpath, "w+")
		exp.write(". /home/oracle/scripts/oracle_env_APEXDB.sh\nexpdp parfile={}".format(par_file_fullpath))
		exp.close()
	
		# Opening the export command file in read + mode
		exp=open(export_command_file_fullpath, "r+")

		# Assigning the content of the export command file to a Variable
		exp_file_content=exp.read()
		
		# Printing the content of the export command file to standard output
		print(exp_file_content)

		# Making the export command file executable
		os.popen("chmod 700 {}".format(export_command_file_fullpath))
		
		# Running the export command file
		running_command=subprocess.run(["/bin/bash", export_command_file_fullpath])	
		
		# Variable declaration
		STATUS_INS = status_after_job_run
		Time_after_job_run = datetime.datetime.now()
		Time_after_job_run_formated = Time_after_job_run.strftime("%d-%b-%y %I:%M:%S %p")
		OP_ENDTIME_INS = Time_after_job_run_formated

		# Calling the db connection function to log the endtime and update the status of the database backup
		db_connection(args15=STATUS_INS, args11=OP_NAME_INS, args12=OP_STARTTIME_INS, args14= RUNNER_INS, args16=OP_TYPE_INS, args17=OP_ENDTIME_INS)

		# Variable declaration to Send Email for a succesful backup
		TO_EMAIL="stackcloud11@mkitconsulting.net"
		SUBJECT="Successfull Database Backup Ola"
		BODY= "The schema was succesfully exported"
		FROM="oracle@MKIT-DEV-OEM.localdomain"

		# Calling the email function
		STACK_EMAIL(TO_EMAIL, SUBJECT, BODY, FROM)
							
		
	except:
	
		print("Database backup failed")

		# Variable declaration
		STATUS_INS = status_job_error
		Time_after_job_run = datetime.datetime.now()
		Time_after_job_run_formated = Time_after_job_run.strftime("%d-%b-%y %I:%M:%S %p")
		OP_ENDTIME_INS = Time_after_job_run_formated
		
		# Calling the db connection function to log the endtime and update the status of the database backup
		db_connection(args15=STATUS_INS, args11=OP_NAME_INS, args12=OP_STARTTIME_INS, args14= RUNNER_INS, args16=OP_TYPE_INS, args17=OP_ENDTIME_INS)
		
		# Variable declaration to Send Email for a succesful backup
		TO_EMAIL="stackcloud11@mkitconsulting.net"
		SUBJECT="Database Backup failed Ola"
		BODY="The schema " + args["args1"] +  " was not exported"
		FROM="oracle@MKIT-DEV-OEM.localdomain"

		# Calling the email function
		STACK_EMAIL(TO_EMAIL, SUBJECT, BODY, FROM)
		

def f_d_copy(**args):

	# Variable declaration
	current_datetime=datetime.datetime.now()
	current_datetime_formated=current_datetime.strftime("%d-%b-%y %I:%M:%S %p")
	status = ["Running","Completed", "Error"]
	status_before_job_run, status_after_job_run, status_job_error = status
	STATUS_INS = status_before_job_run
	OP_NAME_INS = OP_NAME_INS=args['args11']
	OP_STARTTIME_INS = current_datetime_formated
	RUNNER_INS = sys.argv[4]
	OP_TYPE_INS = sys.argv[5]
	OP_ENDTIME_INS = current_datetime_formated


	# Calling the db connectivity function
	db_connection(args15=STATUS_INS, args11=OP_NAME_INS, args12=OP_STARTTIME_INS, args14= RUNNER_INS, args16=OP_TYPE_INS, args17=OP_ENDTIME_INS)

	try:
		# Printing to standard output the file/directory to copy and the destination path
		print("Copying {} to {}".format(args["args1"], args["args2"]))
		
		if os.path.isfile(args["args1"]):
	
			# Copying files
			shutil.copy(args["args1"], args["args2"])

		else:
					
			# Copying directory
			shutil.copytree(args["args1"], args["args2"])

		# Stating the the copy was successful
		print("{} was successfully copied to {}".format(args["args1"], args["args2"]))

		# Variable declaration
		STATUS_INS = status_after_job_run
		Time_after_job_run = datetime.datetime.now()
		Time_after_job_run_formated = Time_after_job_run.strftime("%d-%b-%y %I:%M:%S %p")
		OP_ENDTIME_INS = Time_after_job_run_formated

		# Calling the db connectivity function
		db_connection(args15=STATUS_INS, args11=OP_NAME_INS, args12=OP_STARTTIME_INS, args14= RUNNER_INS, args16=OP_TYPE_INS, args17=OP_ENDTIME_INS)

		# Variable declaration to Send Email for a succesful copy
		TO_EMAIL="stackcloud11@mkitconsulting.net"
		SUBJECT="Successful file or directory copy Ola"
		BODY="The file or directory {} was successfully copied to {}".format(args["args1"], args["args2"])
		FROM="oracle@MKIT-DEV-OEM.localdomain"

		# Calling the email function
		STACK_EMAIL(TO_EMAIL, SUBJECT, BODY, FROM)		
		
		

	except Exception:
		print("Copy command failed:")
		print(traceback.format_exc())

		# Variable declaration
		STATUS_INS = status_job_error
		Time_after_job_run = datetime.datetime.now()
		Time_after_job_run_formated = Time_after_job_run.strftime("%d-%b-%y %I:%M:%S %p")
		OP_ENDTIME_INS = Time_after_job_run_formated

		
		# Calling the db connection function to log the endtime and update the status of the database backup
		db_connection(args15=STATUS_INS, args11=OP_NAME_INS, args12=OP_STARTTIME_INS, args14= RUNNER_INS, args16=OP_TYPE_INS, args17=OP_ENDTIME_INS)


		# Variable declaration to Send Email for an unsuccesful copy
		TO_EMAIL="stackcloud11@mkitconsulting.net"
		SUBJECT="File/Directory copy failed Ola"
		BODY="The file {} was not copied to the specified destination".format(args["args1"])
		FROM="oracle@MKIT-DEV-OEM.localdomain"

		# Calling the email function
		STACK_EMAIL(TO_EMAIL, SUBJECT, BODY, FROM)


def disk_maintenance_check_on_prem(**args):
	
	try:

		# printing the disk we are checking to standard output
		print("Checking disk usage for {}".format(args["args1"]))

		# Assigning a variable to the disk utilization function
		
		disk_space=shutil.disk_usage(args["args1"])

		# Extracting and printing the value for total, used and free space
		Total_disk_space=disk_space[0]
		print("The total disk space is {}".format(Total_disk_space))

		Used_disk_space=disk_space[1]
		print("The used disk space is {}".format(Used_disk_space))

		free_disk_space=disk_space[2]
		print("The free disk space is {}".format(free_disk_space))

		# Calculating and printing the use percent
		use_percent =(Used_disk_space/Total_disk_space)* 100
		print("The use percent is {}".format(use_percent))
	
 
		# Checking if disk utilization is above threshold
		while 2 > 1:

			if use_percent > int(args["args3"]):
			
				# printing a message to standard output if disk utilization is above threshold
				print("Disk utilization is above critical threshold!")

				# Variable declaration to Send Email for an unsuccesful copy
				TO_EMAIL="stackcloud11@mkitconsulting.net"
				SUBJECT="Disk utilization is above critical Threshold! Ola"
				BODY="The disk utilization for is above the Critical Threshold!"
				FROM="oracle@MKIT-DEV-OEM.localdomain"

				# Calling the email function
				STACK_EMAIL(TO_EMAIL, SUBJECT, BODY, FROM)

				# Setting the time to alert the user
				time.sleep(60)

			elif use_percent > int(args["args2"]):
				print("Disk utilization is above warning threshold!")

				# Variable declaration to Send Email for an unsuccesful copy
				TO_EMAIL="stackcloud11@mkitconsulting.net"
				SUBJECT="Disk utilization is above the warning Threshold!!! Ola"
				BODY="The disk utilization for is above warning Threshold!!!"
				FROM="oracle@MKIT-DEV-OEM.localdomain"
			
				# Calling the email function
				STACK_EMAIL(TO_EMAIL, SUBJECT, BODY, FROM)

				# Setting the time to alert the user
				time.sleep(300)
			
			else:
				print("The disk usage is under the specified threshold ")
				break

	except:
		print("Disk utilization check failed")
		
		# Variable declaration to Send Email for an unsuccesful copy
		TO_EMAIL="stackcloud11@mkitconsulting.net"
		SUBJECT="Disk utilization check failed"
		BODY="Disk utilization check failed"
		FROM="oracle@MKIT-DEV-OEM.localdomain"
		
		# Calling the email function
		STACK_EMAIL(TO_EMAIL, SUBJECT, BODY, FROM)


def G_Zipp(**args):

	try:
		# Variable declaration
		stamped_zipped_file="{}_{}.gz".format(args["args1"], TS)
			
		# Stating the file to Zip up
		print("Zipping up {}".format(args["args1"]))
	
		# Opening the file to be zipped in read binary mode
		zip_in = open(args["args1"], "rb")
		print("{} opened in read binary mode".format(args["args1"]))
	
		# Creating a zip file in write binary mode
		zip_out = gzip.open(stamped_zipped_file, "wb")
		print("{} opened in write binary mode".format(stamped_zipped_file))

		# Copying content of the unzipped file to the zipped file
		shutil.copyfileobj(zip_in, zip_out)

		# Stating the zip file created
		print("{} has been successfully created".format(stamped_zipped_file))

		# Variable declaration to Send Email for a successful zip
		TO_EMAIL="stackcloud11@mkitconsulting.net"
		SUBJECT="Successful Gzip Ola"
		BODY="The file " + args["args1"] + " was successfully zipped"
		FROM="oracle@MKIT-DEV-OEM.localdomain"

		# Calling the email function
		STACK_EMAIL(TO_EMAIL, SUBJECT, BODY, FROM)

	except:
		print("Gzip failed")

		# Variable declaration to Send Email for a successful zip
		TO_EMAIL="stackcloud11@mkitconsulting.net"
		SUBJECT="Gzip failed Ola"
		BODY="Gzip failed Ola"
		FROM="oracle@MKIT-DEV-OEM.localdomain"

		# Calling the email function
		STACK_EMAIL(TO_EMAIL, SUBJECT, BODY, FROM)



def unzip_gzipp(**args):

	try:

		# Variable declaration
	
		os.path.splitext(args["args1"])
		unzipped_file=os.path.splitext(args["args1"])[0]
		print(unzipped_file)

		# Stating the file to be unzipped
		print("Unzipping" + args["args1"])
	
		# Opening the file to unzip in read binary mode
		gu_in=gzip.open(args["args1"], "rb")
	
		# Creating the unzipped file in write binary mode
		gu_out=open(unzipped_file, "wb")

		# Copying the content of the zipped file to the unzipped file
		new_file=shutil.copyfileobj(gu_in, gu_out)

		# Closing file_to_unzip
		gu_in.close()

		# Closing unzipped_file
		gu_out.close()

		# Stating that the unzipped file has been created
		print("{} has been successfully unzipped".format(args["args1"]))

		return unzipped_file
		
		# Variable declaration to Send Email for a successful zip
		TO_EMAIL="stackcloud11@mkitconsulting.net"
		SUBJECT="Gzip failed Ola"
		BODY="Gzip failed Ola for file " + args["args1"]
		FROM="oracle@MKIT-DEV-OEM.localdomain"

		# Calling the email function
		STACK_EMAIL(TO_EMAIL, SUBJECT, BODY, FROM)

		#return unzipped_file

	except:
		print("File unzip failed")

		# Variable declaration to Send Email for a successful zip
		TO_EMAIL="stackcloud11@mkitconsulting.net"
		SUBJECT="Gzip failed Ola"
		BODY="Gzip failed Ola"
		FROM="oracle@MKIT-DEV-OEM.localdomain"

		# Calling the email function
		STACK_EMAIL(TO_EMAIL, SUBJECT, BODY, FROM)



def database_import(**args):	


		
	# Variable declaration
	file_base_path="/home/oracle/scripts/practicedir_ola_sep23"
	imp_parfile_name="impdp_" + args["args1"] + "_stack_" + args["args2"] + ".par"
	imp_parfile_path=os.path.join(file_base_path, imp_parfile_name)
	user="'/ as sysdba'"
	#migrated_schema=args["args1"] + ":stack_" + args["args2"] + "_migrated"
	migrated_schema=args["args1"] + ":stack_" + args["args2"] + "_migrated"
	#dumpfile=args["args1"] + "_" + args["args2"] + "_" + TS + ".dmp"	
	dumpfile = args['args4']
	logfile=args["args1"] + "_" + args["args2"] + "_" + TS + ".log"
	import_command_file="import.sh"
	imp_command_fullpath=os.path.join(file_base_path, import_command_file)
	exp_backup_path="/backup/AWSSEP23/APEXDB"
	imp_backup_path="/backup/AWSSEP23/SAMD/"
	exp_dumpfile_fullpath=os.path.join(exp_backup_path, dumpfile)
	imp_dumpfile_fullpath=os.path.join(imp_backup_path, dumpfile)
	#dmp_basename=os.path.basename(args["args2"])
	status = ["Running","Completed", "Error"]
	status_before_job_run, status_after_job_run, status_job_error = status
	STATUS_INS = status_before_job_run
	current_datetime=datetime.datetime.now()
	current_datetime_formated=current_datetime.strftime("%d-%b-%y %I:%M:%S %p")
	OP_NAME_INS = args['args11']
	OP_STARTTIME_INS= current_datetime_formated
	OP_ENDTIME_INS = current_datetime_formated
	RUNNER_INS = args['args14']
	OP_TYPE_INS = args['args16']
		

	# Calling the db connection function 
	db_connection(args15=STATUS_INS, args11=OP_NAME_INS, args12=OP_STARTTIME_INS, args14= RUNNER_INS, args16=OP_TYPE_INS, args17=OP_ENDTIME_INS)

	try:
		
		# Printing the full path to the provided dumpfile
		print("The fullpath of the exported dmp file is {}".format(exp_dumpfile_fullpath))
	
		
		# Copying the unzipped dmp file to the physical path of the database import location
		shutil.copy(exp_dumpfile_fullpath, imp_backup_path)		
		print("dumpfile successfully copied")
			
		# Creating and printing fullpath of the copied dmp file 
		imp_dumpfile_fullpath=os.path.join(imp_backup_path, dumpfile)

		# Checking the file exist in the import location
		if imp_dumpfile_fullpath:
			print("The  dumpfile was successfully copied to the import location. Fullpath: {}".format(imp_dumpfile_fullpath))
		
		# Creating the import parfile in write and read mode
		im=open(imp_parfile_path, "w+") 

		# Writing into the import parameter file
		im.write("userid=" + user + "\nschemas=" + args["args1"] + "\nremap_schema=" + migrated_schema + "\ndumpfile=" + dumpfile + "\nlogfile=" + logfile + "\ndirectory=" + args["args3"] + "\ntable_exists_action=replace")
		
		# Closing the import parameter file
		im.close()
			
		# Opening the import parameter file in read plus mode
		im=open(imp_parfile_path, "r+")

		# Assigning the content of the parameter file to a variable and reading the content
		im_content=im.read()

		# Printing the content of the import parameter file
		print(im_content)

		# Closing the import parmeter file
		im.close()

		# Confirming the import parameter file was created
		if imp_parfile_path:
			print("Import parameter file was successfully created")
	
		# Setting the envinronment variable and creating an import command file
		imp=open(imp_command_fullpath, "w+")

		#Setting the envinronment variable and writing the import command 
		imp.write(". /home/oracle/scripts/oracle_env_SAMD.sh\nimpdp parfile={}".format(imp_parfile_path))
		
		# Closing the import command file
		imp.close()

		# Opening the import command file in read plus mode
		imp=open(imp_command_fullpath, "r+")

		# Assigning the content of the inport command file to a variable and reading the content
		imp_command_content=imp.read()

		# Printing the content of the import command file
		print(imp_command_content)

		# Closing the import command file
		imp.close()

		# Confirming the import command file is created
		if imp_command_fullpath:
			print("Import command file was successfully created")

		# Making the import command file executable
		os.popen("chmod 700 {}".format(imp_command_fullpath))

			
		# Running the import.sh file	
		run_command=subprocess.run(["/bin/bash", imp_command_fullpath])	

		# Variable declaration
		STATUS_INS = status_after_job_run
		Time_after_job_run = datetime.datetime.now()
		Time_after_job_run_formated = Time_after_job_run.strftime("%d-%b-%y %I:%M:%S %p")
		OP_ENDTIME_INS = Time_after_job_run_formated

		# Calling the db connection function to log the endtime and update the status of the import
		db_connection(args15=STATUS_INS, args11=OP_NAME_INS, args12=OP_STARTTIME_INS, args14= RUNNER_INS, args16=OP_TYPE_INS, args17=OP_ENDTIME_INS)

		# Variable declaration for sending a mail
		TO_EMAIL="stackcloud11@mkitconsulting.net"
		SUBJECT="Database Import successfully completed Ola"
		BODY="The dumpfile was successfully imported"
		FROM="oracle@MKIT-DEV-OEM.localdomain"

		# Calling the email function
		STACK_EMAIL(TO_EMAIL, SUBJECT, BODY, FROM)

		
	except Exception:
		print("Database import failed")
		print(traceback.format_exc())
		
		# Variable declaration
		STATUS_INS = status_job_error
		Time_after_job_run = datetime.datetime.now()
		Time_after_job_run_formated = Time_after_job_run.strftime("%d-%b-%y %I:%M:%S %p")
		OP_ENDTIME_INS = Time_after_job_run_formated

		# Calling the db connection function to log the endtime and update the status of the import
		db_connection(args15=STATUS_INS, args11=OP_NAME_INS, args12=OP_STARTTIME_INS, args14= RUNNER_INS, args16=OP_TYPE_INS, args17=OP_ENDTIME_INS)


		# Variable declaration for sending a mail
		TO_EMAIL="stackcloud11@mkitconsulting.net"
		SUBJECT="File Successfully Copied Ola"
		BODY="The file {} was succesfully copied"
		FROM="oracle@MKIT-DEV-OEM.localdomain"

		# Calling the email function
		STACK_EMAIL(TO_EMAIL, SUBJECT, BODY, FROM)
		

def data_migration(**args):

	# Variables
	OP_NAME_INS = args["args11"]
	schema = args["args1"] 
	runner= args["args2"] 
	directory = args["args3"]
	OP_TYPE_INS = args["args16"]
	dumpfile=args["args1"] + "_" + args["args2"] + "_" + TS + ".dmp"
	logfile=args["args1"] + "_" + args["args2"] + "_" + TS + ".log"
	current_datetime=datetime.datetime.now()
	current_datetime_formated=current_datetime.strftime("%d-%b-%y %I:%M:%S %p")
	status = ["Running","Completed", "Error"]
	status_before_job_run, status_after_job_run, status_job_error = status
	STATUS_INS = status_before_job_run
	OP_STARTTIME_INS = current_datetime_formated
	OP_ENDTIME_INS = current_datetime_formated
	RUNNER_INS = runner
	file_base_path="/home/oracle/scripts/practicedir_ola_sep23"
	imp_parfile_name="impdp_" + args["args1"] + "_stack_" + args["args2"] + ".par"
	imp_parfile_path=os.path.join(file_base_path, imp_parfile_name)
	user="'/ as sysdba'"
	migrated_schema=args["args1"] + ":stack_" + args["args2"] + "_migrated"
	import_command_file="import.sh"
	imp_command_fullpath=os.path.join(file_base_path, import_command_file)
	exp_backup_path="/backup/AWSSEP23/APEXDB"
	imp_backup_path="/backup/AWSSEP23/SAMD/"
	exp_dumpfile_fullpath=os.path.join(exp_backup_path, dumpfile)
	imp_dumpfile_fullpath=os.path.join(imp_backup_path, dumpfile)


	
	# Calling the db connectivity function
	db_connection(args15=STATUS_INS, args11=OP_NAME_INS, args12=OP_STARTTIME_INS, args14= RUNNER_INS, args16=OP_TYPE_INS, args17=OP_ENDTIME_INS)


	try:
		# Calling the database backup function
		database_backup(args1=schema, args2=runner, args3=directory, args15=STATUS_INS, args11=OP_NAME_INS, args12=OP_STARTTIME_INS, args14= RUNNER_INS, args16=OP_TYPE_INS, args17=OP_ENDTIME_INS)
		
		# Copying the exported dmp to the import physical path
		shutil.copy(exp_dumpfile_fullpath, imp_dumpfile_fullpath)

		# Creating the import parfile in write and read mode
		im=open(imp_parfile_path, "w+")
		
		# Writing into the import parameter file
		im.write("userid=" + user + "\nschemas=" + args["args1"] + "\nremap_schema=" + migrated_schema + "\ndumpfile=" + dumpfile + "\nlogfile=" + logfile + "\ndirectory=" + args["args3"] + "\ntable_exists_action=replace")

		# Closing the import parameter file
		im.close()

		# Opening the import parameter file in read plus mode
		im=open(imp_parfile_path, "r+")
		
		# Assigning the content of the parameter file to a variable and reading the content
		im_content=im.read()
	
		# Printing the content of the import parameter file
		print(im_content)

		# Closing the import parmeter file
		im.close()

		# Confirming the import parameter file was created
		if imp_parfile_path:
			print("Import parameter file was successfully created")

		# Setting the envinronment variable and creating an import command file
		imp=open(imp_command_fullpath, "w+")

		#Setting the envinronment variable and writing the import command
		imp.write(". /home/oracle/scripts/oracle_env_SAMD.sh\nimpdp parfile={}".format(imp_parfile_path))

		# Closing the import command file
		imp.close()

		# Opening the import command file in read plus mode
		imp=open(imp_command_fullpath, "r+")

		# Assigning the content of the inport command file to a variable and reading the content
		imp_command_content=imp.read()

		# Printing the content of the import command file
		print(imp_command_content)

		# Closing the import command file
		imp.close()

		# Confirming the import command file is created
		if imp_command_fullpath:
			print("Import command file was successfully created")

		# Making the import command file executable
		os.popen("chmod 700 {}".format(imp_command_fullpath))

		# Running the import.sh file
		run_command=subprocess.run(["/bin/bash", imp_command_fullpath])

		# Variable declaration
		STATUS_INS = status_after_job_run
		Time_after_job_run = datetime.datetime.now()
		Time_after_job_run_formated = Time_after_job_run.strftime("%d-%b-%y %I:%M:%S %p")
		OP_ENDTIME_INS = Time_after_job_run_formated

		# Calling the db connectivity function
		db_connection(args15=STATUS_INS, args11=OP_NAME_INS, args12=OP_STARTTIME_INS, args14= RUNNER_INS, args16=OP_TYPE_INS, args17=OP_ENDTIME_INS)

	except Exception:
		print("Data Migration failed")
		print(traceback.format_exc())
	
		# Variable declaration
		STATUS_INS = status_job_error
		Time_after_job_run = datetime.datetime.now()
		Time_after_job_run_formated = Time_after_job_run.strftime("%d-%b-%y %I:%M:%S %p")
		OP_ENDTIME_INS = Time_after_job_run_formated

		# Calling the db connection function to log the endtime and update the status of the database backup
		db_connection(args15=STATUS_INS, args11=OP_NAME_INS, args12=OP_STARTTIME_INS, args14= RUNNER_INS, args16=OP_TYPE_INS, args17=OP_ENDTIME_INS)


def aws_create_user(**args):

	# Variable declaration:
	current_datetime=datetime.datetime.now()
	current_datetime_formated=current_datetime.strftime("%d-%b-%y %I:%M:%S %p")
	status = ["Running","Completed", "Error"]
	status_before_job_run, status_after_job_run, status_job_error = status
	STATUS_INS = status_before_job_run
	OP_NAME_INS = "IAM"
	OP_STARTTIME_INS = current_datetime_formated
	OP_ENDTIME_INS = current_datetime_formated
	RUNNER_INS = "Stackprog_ola"
	OP_TYPE_INS	= "AWS"	

	try:
		# Calling the db connectivity function to log activity information before user creation
		db_connection(args15=STATUS_INS, args11=OP_NAME_INS, args12=OP_STARTTIME_INS, args14= RUNNER_INS, args16=OP_TYPE_INS, args17=OP_ENDTIME_INS)
		
		# Stating the AWS service 		
		iam = boto3.client(args['service'], aws_access_key_id = p.Access_key_ID, aws_secret_access_key = p.Secret_access_key)
		
		try:

			# Checking if user already exists
			getting_username=iam.get_user(UserName = args['user'])
		
			if getting_username['User']['UserName'] == args['user']:
				print("User already exists.")

			else:
				("Creating a user")

		except:

				# Creating an IAM user
				response = iam.create_user(UserName = args['user'])

		# Variable Declaration
		STATUS_INS = status_after_job_run
		Time_after_job_run = datetime.datetime.now()
		Time_after_job_run_formated = Time_after_job_run.strftime("%d-%b-%y %I:%M:%S %p")
		OP_ENDTIME_INS = Time_after_job_run_formated

		# Calling the function to update opetartions table after user creation
		db_connection(args15=STATUS_INS, args11=OP_NAME_INS, args12=OP_STARTTIME_INS, args14= RUNNER_INS, args16=OP_TYPE_INS, args17=OP_ENDTIME_INS)

	except ClientError as error:
		print(error.response)

		print("An error occured: User not created")

		# Variable declaration
		STATUS_INS = status_job_error
		Time_after_job_run = datetime.datetime.now()
		Time_after_job_run_formated = Time_after_job_run.strftime("%d-%b-%y %I:%M:%S %p")
		OP_ENDTIME_INS = Time_after_job_run_formated


		# Calling the db connection function to log the endtime and update the status with an error message
		db_connection(args15=STATUS_INS, args11=OP_NAME_INS, args12=OP_STARTTIME_INS, args14= RUNNER_INS, args16=OP_TYPE_INS, args17=OP_ENDTIME_INS)



def create_aws_group(**args):

		
	try:
		# Variable declaration
		current_datetime=datetime.datetime.now()
		current_datetime_formated=current_datetime.strftime("%d-%b-%y %I:%M:%S %p")
		status = ["Running","Completed", "Error"]
		status_before_job_run, status_after_job_run, status_job_error = status
		STATUS_INS = status_before_job_run
		OP_NAME_INS = "IAM"
		OP_STARTTIME_INS = current_datetime_formated
		RUNNER_INS = "Stackprog_ola"
		OP_TYPE_INS = "AWS"
		OP_ENDTIME_INS = current_datetime_formated


		# Calling the db_connection function to write activity into the database
		db_connection(args15=STATUS_INS, args11=OP_NAME_INS, args12=OP_STARTTIME_INS, args14= RUNNER_INS, args16=OP_TYPE_INS, args17=OP_ENDTIME_INS)

		# Stating the AWS service
		iam = boto3.client(args['service'], aws_access_key_id = p.Access_key_ID, aws_secret_access_key = p.Secret_access_key)

		try:

			# Checking if group already exists
			getting_group = iam.get_group(GroupName = args['GroupName'])
			print(getting_group)

			if getting_group['Group']['GroupName'] == args['GroupName']:
				print("Group already exists. Checking if user exists")

			else:
				print("Creating a group")

		except:

			# Creating user group
			create_group_response = iam.create_group(GroupName = args['GroupName'])


			# Attaching policy to the group:
			attach_policy_response = iam.attach_group_policy(GroupName = args['GroupName'], PolicyArn = "arn:aws:iam::aws:policy/AdministratorAccess")	

		# Variable Declaration
		STATUS_INS = status_after_job_run
		Time_after_job_run = datetime.datetime.now()
		Time_after_job_run_formated = Time_after_job_run.strftime("%d-%b-%y %I:%M:%S %p")
		OP_ENDTIME_INS = Time_after_job_run_formated
	
		# Calling the function to update opetartions table after group creation
		db_connection(args15=STATUS_INS, args11=OP_NAME_INS, args12=OP_STARTTIME_INS, args14= RUNNER_INS, args16=OP_TYPE_INS, args17=OP_ENDTIME_INS)

	except ClientError as error:
		print(error.create_group_response)

		if error.create_group_response:
			print("Error while attempting to create group")

		if error.attach_policy_response['Error']['Code'] == "NoSuchEntity":
			print("Policy not properly stated")

		else:
			print("Error while attaching policy to group")

		# Variable declaration
		STATUS_INS = status_job_error
		Time_after_job_run = datetime.datetime.now()
		Time_after_job_run_formated = Time_after_job_run.strftime("%d-%b-%y %I:%M:%S %p")
		OP_ENDTIME_INS = Time_after_job_run_formated

		
		# Calling the db connection function to log the endtime and update the status with an error message
		db_connection(args15=STATUS_INS, args11=OP_NAME_INS, args12=OP_STARTTIME_INS, args14= RUNNER_INS, args16=OP_TYPE_INS, args17=OP_ENDTIME_INS)


def attach_user_to_group(**args):

	try:
		# Variable declaration
		current_datetime=datetime.datetime.now()
		current_datetime_formated=current_datetime.strftime("%d-%b-%y %I:%M:%S %p")
		status = ["Running","Completed", "Error"]
		status_before_job_run, status_after_job_run, status_job_error = status
		STATUS_INS = status_before_job_run
		OP_NAME_INS = "IAM"
		OP_STARTTIME_INS = current_datetime_formated
		OP_ENDTIME_INS = current_datetime_formated
		RUNNER_INS = "Stackprog_ola"
		OP_TYPE_INS = "AWS"


		# Calling the db connectivity function to log activity information before user creation
		db_connection(args15=STATUS_INS, args11=OP_NAME_INS, args12=OP_STARTTIME_INS, args14= RUNNER_INS, args16=OP_TYPE_INS, args17=OP_ENDTIME_INS)

		# Stating the AWS service
		iam = boto3.client(args['service'], aws_access_key_id = p.Access_key_ID, aws_secret_access_key = p.Secret_access_key)

		# Attaching policy to the group
		attach_user_response = iam.add_user_to_group(UserName = args['UserName'], GroupName= args['GroupName'])

		# Creating a login profile
		login_response = iam.create_login_profile(UserName = args['UserName'], Password = new_user_password, PasswordResetRequired = True)

		# Variable Declaration
		STATUS_INS = status_after_job_run
		Time_after_job_run = datetime.datetime.now()
		Time_after_job_run_formated = Time_after_job_run.strftime("%d-%b-%y %I:%M:%S %p")
		OP_ENDTIME_INS = Time_after_job_run_formated

		# Calling the function to update opetartions table after user creation
		db_connection(args15=STATUS_INS, args11=OP_NAME_INS, args12=OP_STARTTIME_INS, args14= RUNNER_INS, args16=OP_TYPE_INS, args17=OP_ENDTIME_INS)


	except ClientError as error:

		if error.attach_user_response['Error']['Code'] == "NoSuchEntity":
			print(error.attach_user_response)
			print("User doesnt not exist")

		else:
			print("Error: Unable to attach user to a group")

		if error.login_response['Error']['Code'] == "EntityAlreadyExists":
			print(error.login_response)
			print("User exist already")

		else:
			print("Error: Unable to attach user to group")

		# Variable declaration
		STATUS_INS = status_job_error
		Time_after_job_run = datetime.datetime.now()
		Time_after_job_run_formated = Time_after_job_run.strftime("%d-%b-%y %I:%M:%S %p")
		OP_ENDTIME_INS = Time_after_job_run_formated


		# Calling the db connection function to log the endtime and update the status with an error message

		db_connection(args15=STATUS_INS, args11=OP_NAME_INS, args12=OP_STARTTIME_INS, args14= RUNNER_INS, args16=OP_TYPE_INS, args17=OP_ENDTIME_INS)




def Migrate_On_Prem_Users(**kwargs):
	
	try:

		# Variable declaration
		current_datetime=datetime.datetime.now()
		current_datetime_formated=current_datetime.strftime("%d-%b-%y %I:%M:%S %p")
		status = ["Running","Completed", "Error"]
		status_before_job_run, status_after_job_run, status_job_error = status
		STATUS_INS = status_before_job_run
		OP_NAME_INS = kwargs['OP_NAME_INS']
		OP_STARTTIME_INS = current_datetime_formated
		OP_ENDTIME_INS = current_datetime_formated
		RUNNER_INS = kwargs['RUNNER_INS']
		OP_TYPE_INS = kwargs['OP_TYPE_INS']


		# Calling the db connectivity function to log activity information before user creation
		db_connection(args15=STATUS_INS, args11=OP_NAME_INS, args12=OP_STARTTIME_INS, args14= RUNNER_INS, args16=OP_TYPE_INS, args17=OP_ENDTIME_INS)


		# Stating the AWS service
		iam = boto3.client(kwargs['service'], aws_access_key_id = p.Access_key_ID, aws_secret_access_key = p.Secret_access_key)
		

		# Calling the AWS create group funtion
		create_aws_group(service="iam", GroupName=sys.argv[2])

		# Connecting into the database with our connection details
		connection=c.connect(user="STACK_OLA_SEP23", password=p.db_password, dsn=p.APEXDB_dsn)

		# Defining the cursor
		cursor=connection.cursor()

		# Read usernames ending in SEP23
		cursor.execute("""select username from all_users where username like '%SEP23'""")

		usernames = cursor.fetchall()

		for names in usernames:
			extracted_name=names[0]
			print(extracted_name)
				
			# creating the AWS IAM user 
			create_user = iam.create_user(UserName = extracted_name)
			print("The user {} was successdully created".format(extracted_name))		

			#Creating login profile for user
			create_login = iam.create_login_profile(UserName = extracted_name, Password =p.new_user_password, PasswordResetRequired = True)
			print("Login profile successfully created for {}".format(extracted_name))

			# Attaching user to group function
			attach_user = iam.add_user_to_group(GroupName = kwargs['GroupName'], UserName = extracted_name)
			print("The user {} was sucessfully added to group {}".format(extracted_name, kwargs['GroupName']))			

		# Variable Declaration

		STATUS_INS = status_after_job_run
		Time_after_job_run = datetime.datetime.now()
		Time_after_job_run_formated = Time_after_job_run.strftime("%d-%b-%y %I:%M:%S %p")
		OP_ENDTIME_INS = Time_after_job_run_formated


		# Calling the function to update opetartions table after user creation
		db_connection(args15=STATUS_INS, args11=OP_NAME_INS, args12=OP_STARTTIME_INS, args14= RUNNER_INS, args16=OP_TYPE_INS, args17=OP_ENDTIME_INS)
	
	except ClientError as error:

		# Variable declaration
		STATUS_INS = status_job_error
		Time_after_job_run = datetime.datetime.now()
		Time_after_job_run_formated = Time_after_job_run.strftime("%d-%b-%y %I:%M:%S %p")
		OP_ENDTIME_INS = Time_after_job_run_formated

		# Calling the db connection function to log the endtime and update the status with an error message

		db_connection(args15=STATUS_INS, args11=OP_NAME_INS, args12=OP_STARTTIME_INS, args14= RUNNER_INS, args16=OP_TYPE_INS, args17=OP_ENDTIME_INS)

		print(error)

		if error.response['Error']['Code'] == "NoSuchEntity":
			print("User doesnt not exist")

		else:
			print("Error: Unable to attach user to a group")



def create_s3_bucket(**kwargs):
	
	try:

		# Stating the AWS service we are calling before we can assume the role
		sts = boto3.client('sts', aws_access_key_id = p.Access_key_ID, aws_secret_access_key = p.Secret_access_key)

	
		# Calling the Assume role to assume the Engineer role from the management account
		response_assume_role = sts.assume_role(
			RoleArn = kwargs['RoleArn'],
			RoleSessionName = "s3-Engineer-Dev"
		) 

		AccessKeyId = response_assume_role['Credentials']['AccessKeyId']
		SecretAccessKey = response_assume_role['Credentials']['SecretAccessKey']
		SessionToken = response_assume_role['Credentials']['SessionToken']


		# Using the temporary credentials from the assume role to connect to amazon s3 resource
	
		s3 = boto3.client('s3', aws_access_key_id = AccessKeyId, aws_secret_access_key = SecretAccessKey, aws_session_token = SessionToken)

	
		# Creating a bucket
		s3_bucket = s3.create_bucket(Bucket= kwargs['Bucket'])

	except ClientError as error:
		if error.response['Error']['Code'] == "BucketAlreadyExists":
			print("Bucket already exists")
			
		else:
			print("Error while creating bucket")



def delete_user(**kwargs):
	
	try:

		# Stating the AWS service we are using
		iam = boto3.client(kwargs['service'], aws_access_key_id = p.Access_key_ID, aws_secret_access_key = p.Secret_access_key)

		# Checking if User exists in a group
		getting_users_group = iam.list_groups_for_user(UserName = kwargs['UserName'])
		print(getting_users_group)

		#list_of_groups = []

		list_items = getting_users_group['Groups'][0]['GroupName']
		print(list_items)

		for index in range(len(getting_users_group['Groups'])):
			#print(getting_users_group['Groups'][index]['GroupName'])
			group_list=getting_users_group['Groups'][index]['GroupName']		

		for group in group_list:
			remove_user_from_group = iam.remove_user_from_group(UserName = kwargs['UserName'], GroupName = group_list)

		# Deleting user profile
		delete_profile = iam.delete_login_profile(UserName = kwargs['UserName'])

		# Making the API call to the detele action
		delete_user = iam.delete_user(UserName = kwargs['UserName'])
		print("User {} was successfully deleted".format(kwargs['UserName']))	
	
	except ClientError as error:
		if error.response['Error']['Code']== "DeleteConflict":
			print("User {} has subordinate entities.".format(kwargs['UserName']))

		else:
			print("User could not be deleted")
			print(error.response)


def delete_bucket(**kwargs):

	try:
		# Stating the AWS service we are calling before we can assume the role
		sts = boto3.client('sts', aws_access_key_id = p.Access_key_ID, aws_secret_access_key = p.Secret_access_key)

		# Calling the Assume role to assume the Engineer role from the management account
		response_assume_role = sts.assume_role(
		RoleArn = kwargs['RoleArn'],
		RoleSessionName = "s3-Engineer-Dev"
		)	


		AccessKeyId = response_assume_role['Credentials']['AccessKeyId']
		SecretAccessKey = response_assume_role['Credentials']['SecretAccessKey']
		SessionToken = response_assume_role['Credentials']['SessionToken']

		# Using the temporary credentials from the assume role to connect to amazon s3 resource
		s3 = boto3.client('s3', aws_access_key_id = AccessKeyId, aws_secret_access_key = SecretAccessKey, aws_session_token = SessionToken)

		# Deleting a bucket
		s3_delete_bucket = s3.delete_bucket(Bucket = kwargs['Bucket'])

		print("The bucket {} has been successfully deleted".format(kwargs['Bucket']))

	except ClientError as error:
		print(error)


def upload_s3_bucket(**kwargs):

	try:
		# Stating the AWS service we are calling before we can assume the role
		sts = boto3.client('sts', aws_access_key_id = p.Access_key_ID, aws_secret_access_key = p.Secret_access_key)

		# Calling the Assume role to assume the Engineer role from the management account
		response_assume_role = sts.assume_role(
		RoleArn = kwargs['RoleArn'],
		RoleSessionName = "s3-Engineer-Dev"
		)

		# Getting the temporary credentials
		AccessKeyId = response_assume_role['Credentials']['AccessKeyId']
		SecretAccessKey = response_assume_role['Credentials']['SecretAccessKey']
		SessionToken = response_assume_role['Credentials']['SessionToken']

		# Using the temporary credentials from the assume role to connect to amazon s3 resource
		s3 = boto3.client('s3', aws_access_key_id = AccessKeyId, aws_secret_access_key = SecretAccessKey, aws_session_token = SessionToken)



		# Upload content into a bucket
		files_entered = kwargs['file_to_upload'].split(",") 
		print(files_entered)		
	
			
		for item in files_entered:
			uploaded_file_name = item.split("/")[5]
			print(uploaded_file_name)

			s3.upload_file(item, kwargs['Bucket'], uploaded_file_name)
			print("The file {} has been successfully uploaded".format(uploaded_file_name))

	except ClientError as error:
		print("An error occured, file upload failed")
		print(error)




def empty_S3_bucket(**kwargs):

	try:
		# Stating the AWS service we are calling before we can assume the role
		sts = boto3.client('sts', aws_access_key_id = p.Access_key_ID, aws_secret_access_key = p     .Secret_access_key)

		# Calling the Assume role to assume the Engineer role from the management account
		response_assume_role = sts.assume_role(
		RoleArn = kwargs['RoleArn'],
		RoleSessionName = "s3-Engineer-Dev"
		)


		# Getting the temporary credentials
		AccessKeyId = response_assume_role['Credentials']['AccessKeyId']
		SecretAccessKey = response_assume_role['Credentials']['SecretAccessKey']
		SessionToken = response_assume_role['Credentials']['SessionToken']
		aws_region="us-east-1"
		# Using the temporary credentials from the assume role to connect to amazon s3 resource
		s3 = boto3.client('s3', aws_access_key_id = AccessKeyId, aws_secret_access_key = SecretAccessKey, aws_session_token = SessionToken, region_name=aws_region)


		# Listing object in the bucket before deleting
		list_object_response = s3.list_objects(Bucket=kwargs['Bucket'])
		

		for index in range(len(list_object_response['Contents'])):
			object_in_bucket=list_object_response['Contents'][index]['Key']	
			print(object_in_bucket)
	
			# Deleting object from a bucket
			delete_object_response = s3.delete_object(Bucket=kwargs['Bucket'],Key=object_in_bucket)
			print("{} was successfully deleted".format(object_in_bucket))

	except ClientError as error:

		if error.response['Error']['Code']== "NoSuchBucket":
			print("The Bucket entered does not exist")
	
		else:
			print("An error occured while trying to delete bucket")
			print(error)

	except KeyError:
		print("The bucket contains no object")



def list_s3_bucket(**kwargs):

	try:
		# Stating the AWS service we are calling before we can assume the role
		sts = boto3.client('sts', aws_access_key_id = p.Access_key_ID, aws_secret_access_key = p.Secret_access_key)

		# Calling the Assume role to assume the Engineer role from the management account
		response_assume_role = sts.assume_role(
		RoleArn = kwargs['RoleArn'],
		RoleSessionName = "s3-Engineer-Dev"
		)


		# Getting the temporary credentials
		AccessKeyId = response_assume_role['Credentials']['AccessKeyId']
		SecretAccessKey = response_assume_role['Credentials']['SecretAccessKey']
		SessionToken = response_assume_role['Credentials']['SessionToken']
		aws_region="us-east-1"

		# Using the temporary credentials from the assume role to connect to amazon s3 resource
		s3 = boto3.client('s3', aws_access_key_id = AccessKeyId, aws_secret_access_key = SecretAccessKey, aws_session_token = SessionToken, region_name=aws_region)

		# Listing object in the bucket before deleting
		list_object_response = s3.list_objects(Bucket=kwargs['Bucket'])

		print("The bucket {} contains the following objects:".format(kwargs['Bucket']))

		# Looping through the and printing out the object names
		for index in range(len(list_object_response['Contents'])):
			object_in_bucket=list_object_response['Contents'][index]['Key']
			print(object_in_bucket)


	except ClientError as error:
		if error.response['Error']['Code']== "NoSuchBucket":
			print("The Bucket entered does not exist")

		else:
			print("An error occured while trying to delete bucket")
			print(error)




def s3_bucket_versioning(**kwargs):

	try:
		# Stating the AWS service we are calling before we can assume the role
		sts = boto3.client('sts', aws_access_key_id = p.Access_key_ID, aws_secret_access_key = p.Secret_access_key)

		# Calling the Assume role to assume the Engineer role from the management account
		response_assume_role = sts.assume_role(
		RoleArn = kwargs['RoleArn'],
		RoleSessionName = "s3-Engineer-Dev"
		)

		# Getting the temporary credentials
		AccessKeyId = response_assume_role['Credentials']['AccessKeyId']
		SecretAccessKey = response_assume_role['Credentials']['SecretAccessKey']
		SessionToken = response_assume_role['Credentials']['SessionToken']
		aws_region="us-east-1"

		# Using the temporary credentials from the assume role to connect to amazon s3 resource
		s3 = boto3.client('s3', aws_access_key_id = AccessKeyId, aws_secret_access_key = SecretAccessKey, aws_session_token = SessionToken, region_name=aws_region)


		# Setting up Versionning
		versioning_response = s3.put_bucket_versioning(Bucket=kwargs['Bucket'], VersioningConfiguration={'Status' : kwargs['versioning_status']})

		print("Versioning has been {} for objects in the {} bucket".format( kwargs['versioning_status'], kwargs['Bucket']))


	except ClientError as error:
		print(error)






