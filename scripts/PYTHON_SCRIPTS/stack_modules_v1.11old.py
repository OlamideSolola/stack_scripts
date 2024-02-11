#!/usr/bin/bash

# Import Modules
import time,os,shutil,sys,gzip,smtplib



# Variable declaration
timestring=time.localtime()
TS=time.strftime("%m%d%Y%H%M%S", timestring)


# Function definition
def database_backup(schema, runner, directory):

	# Variable Declaration

	user="'/ as sysdba'"
	dumpfile="{}_{}_{}.dmp".format(schema, runner, TS)
	logfile="{}_{}_{}.log".format(schema, runner, TS)
	base_path="/home/oracle/scripts/practicedir_ola_sep23/"
	par_file_name="export_{}.par_{}".format(schema, TS)
	par_file_fullpath=os.path.join(base_path, par_file_name)
	exp_pysical_path="/backup/AWSSEP23/APEXDB/"
	full_exp_physical_path=os.path.join(exp_pysical_path, runner, TS)
	export_command_file="export.sh"
	export_command_file_fullpath=os.path.join(base_path, export_command_file)
	dumpfile_fullpath=os.path.join(base_path,dumpfile)
	logfile_fullpath=os.path.join(base_path,logfile)

	try:
		# Creating a parameter file in write and read mode
		fo=open(par_file_fullpath, "w+")
	
		# Writing into the parameter file
		fo.write("userid={}\nschemas={}\ndumpfile={}\nlogfile={}\ndirectory={}".format(user, schema, dumpfile, logfile, directory))
	
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
		os.popen(export_command_file_fullpath)
		
		# Creating a directory for the dumpfile and logfile
	
		os.makedirs(full_exp_physical_path)
		
		# Moving the created dumpfile and logfile to the new directory
			
		shutil.move(dumpfile_fullpath, full_exp_physical_path)
		shutil.move(logfile_fullpath, full_exp_physical_path)
	
		# Exiting
		exit()

		# Variable declaration to Send Email for a succesful backup
		TO_EMAIL="stackcloud11@mkitconsulting.net"
		SUBJECT="Successfully Database Backup Ola"
		BODY="The schema {} was succesfully exported".format(schema)
		FROM="oracle@MKIT-DEV-OEM.localdomain"

		# Calling the email function
		STACK_EMAIL(TO_EMAIL, SUBJECT, BODY, FROM)
		
	except:
	
		print("Database backup failed")

		# Variable declaration to Send Email for a succesful backup
		TO_EMAIL="stackcloud11@mkitconsulting.net"
		SUBJECT="Database Backup failed Ola"
		BODY="The schema {} was not exported".format(schema)
		FROM="oracle@MKIT-DEV-OEM.localdomain"		

		# Calling the email function
		STACK_EMAIL(TO_EMAIL, SUBJECT, BODY, FROM)


def f_d_copy(f_d_to_copy, dest_path):

	
	try:
		# Printing to standard output the file/directory to copy and the destination path
		print("Copying {} to {}".format(f_d_to_copy, dest_path))
		
		if os.path.isfile(f_d_to_copy):
	
			# Copying files
			shutil.copy(f_d_to_copy, dest_path)

		else:
					
			# Copying directory
			shutil.copytree(f_d_to_copy, dest_path)

		# Stating the the copy was successful
		print("{} was successfully copied to {}".format(f_d_to_copy, dest_path))


		# Variable declaration to Send Email for a succesful copy
		TO_EMAIL="stackcloud11@mkitconsulting.net"
		SUBJECT="Successful file or directory copy Ola"
		BODY="The file or directory {} was successfully copied to {}".format(f_d_to_copy, dest_path)
		FROM="oracle@MKIT-DEV-OEM.localdomain"

		# Calling the email function
		STACK_EMAIL(TO_EMAIL, SUBJECT, BODY, FROM)

	except:
		print("Copy command failed")


		# Variable declaration to Send Email for an unsuccesful copy
		TO_EMAIL="stackcloud11@mkitconsulting.net"
		SUBJECT="File/Directory copy failed Ola"
		BODY="The file {} was not copied to the specified destination".format(f_d_to_copy)
		FROM="oracle@MKIT-DEV-OEM.localdomain"

		# Calling the email function
		STACK_EMAIL(TO_EMAIL, SUBJECT, BODY, FROM)



def disk_maintenance_check_on_prem(disk_path, threshold):
	
	try:

		# printing the disk we are checking to standard output
		print("Checking disk usage for {}".format(disk_path))

		# Assigning a variable to the disk utilization function
		
		disk_space=shutil.disk_usage(disk_path)

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
		if use_percent > int(threshold):
			
			# printing a message to standard output if disk utilization is above threshold
			print("Disk utilization is above threshold!")
		
			# Variable declaration to Send Email for an unsuccesful copy
			TO_EMAIL="stackcloud11@mkitconsulting.net"
			SUBJECT="Disk utilization is above Threshold! Ola"
			BODY="The disk utilization for {} is above Threshold!".format(disk_path)
			FROM="oracle@MKIT-DEV-OEM.localdomain"

			# Calling the email function
			STACK_EMAIL(TO_EMAIL, SUBJECT, BODY, FROM)
			 

		else:
			print("")

	except:
		print("Disk utilization check failed")

		# Variable declaration to Send Email for an unsuccesful copy
		TO_EMAIL="stackcloud11@mkitconsulting.net"
		SUBJECT="Disk utilization check failed"
		BODY="Disk utilization check failed"
		FROM="oracle@MKIT-DEV-OEM.localdomain"


		# Calling the email function
		STACK_EMAIL(TO_EMAIL, SUBJECT, BODY, FROM)


def G_Zipp(file_to_zip):

	try:
		# Variable declaration
		stamped_zipped_file="{}_{}.gz".format(file_to_zip, TS)
			
		# Stating the file to Zip up
		print("Zipping up {}".format(file_to_zip))
	
		# Opening the file to be zipped in read binary mode
		zip_in = open(file_to_zip, "rb")
		print("{} opened in read binary mode".format(file_to_zip))
	
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
		BODY="{} was successfully zipped".format(file_to_zip)
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



def unzip_gzipp(file_to_unzip):

	try:

		# Variable declaration
		path=file_to_unzip
		os.path.splitext(path)
		unzipped_file=os.path.splitext(path)[0]
		print(unzipped_file)

		# Stating the file to be unzipped
		print("Unzipping {}".format(file_to_unzip))
	
		# Opening the file to unzip in read binary mode
		gu_in=gzip.open(file_to_unzip, "rb")
	
		# Creating the unzipped file in write binary mode
		gu_out=open(unzipped_file, "wb")

		# Copying the content of the zipped file to the unzipped file
		shutil.copyfileobj(gu_in, gu_out)

		# Closing file_to_unzip
		gu_in.close()

		# Closing unzipped_file
		gu_out.close()

		# Stating that the unzipped file has been created
		print("{} has been successfully unzipped".format(file_to_unzip))

		return unzipped_file

		# Variable declaration to Send Email for a successful zip
		TO_EMAIL="stackcloud11@mkitconsulting.net"
		SUBJECT="Gzip failed Ola"
		BODY="Gzip failed Ola"
		FROM="oracle@MKIT-DEV-OEM.localdomain"

		# Calling the email function
		STACK_EMAIL(TO_EMAIL, SUBJECT, BODY, FROM)


	except:
		print("File unzip failed")

		# Variable declaration to Send Email for a successful zip
		TO_EMAIL="stackcloud11@mkitconsulting.net"
		SUBJECT="Gzip failed Ola"
		BODY="Gzip failed Ola"
		FROM="oracle@MKIT-DEV-OEM.localdomain"

		# Calling the email function
		STACK_EMAIL(TO_EMAIL, SUBJECT, BODY, FROM)



def database_import(schema, dumpfile, directory):

	try:
		# Variable declaration
		file_location="/home/oracle/scripts/practicedir_ola_sep23"
		imp_filename="impdp_{}_stack_{}.par".format(schema, runner)
		imp_fullpath=os.path.join(file_location, imp_filename)
		user="'/ as sysdba'"
		logfile="{}_{}".format(schema, TS)
		dumpfile=unzipped_dumpfile
		import_command_file="import.sh"
		imp_command_fullpath=os.path.join(file_location, import_command_file)
		migrated_schema="{}:stack_{}_migrated".format(schema, runner)



		# Calling the unzip gzip function to un zip the dumpfile
		unzipped_dumpfile=unzip_gzipp(file_to_unzip)
		return(unzipped_dumpfile)		

		# Creating the import parfile in write and read mode
		im=open(imp_fullpath, "w+") 

		# Writing into the import parameter file
		im.write("userid={}\nschema={}\nremap_schema={}\ndumpfile={}\nlogfile={}\ndirectory={}\ntable_exists_action=replace".format(user, schema ,migrated_schema, unzipped_dumpfile, logfile, directory))

		# Closing the import parameter file
		im.close()

		# Opening the import parameter file in read plus mode
		im=open(imp_fullpath, "r+")

		# Assigning the content of the parameter file to a variable and reading the content
		im_content=im.read()

		# Printing the content of the import parameter file
		print(im_content)

		# Closing the import parmeter file
		im.close()

		# Confirming the import parameter file was created
		if imp_fullpath:
			print("Import parameter file was successfully created")

		# Setting the envinronment variable and creating an import command file
		imp=open(imp_command_fullpath, "w+")

		# Writing into the import command file
		imp.write("export ORACLE_HOME=/u01/app/oracle/product/12.1.0/db_1\nexport ORACLE_SID=SAMD\n/u01/app/oracle/product/12.1.0/db_1/bin/impdp parfile=imp_command_fullpath")
		
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

		# Making the import command file executable
		os.popen("chmod 700 {}".format(imp_command_fullpath))

	
		# Running the import.sh file
		os.popen(imp_command_fullpath)

		# Variable
		TO_EMAIL="stackcloud11@mkitconsulting.net"
		SUBJECT="File Successfully Copied Ola"
		BODY="The file {} was succesfully copied"
		FROM="oracle@MKIT-DEV-OEM.localdomain"
		
		# Calling the email function
		t.STACK_EMAIL(TO_EMAIL, SUBJECT, BODY, FROM)

	except:
		print("Database import failed")
		# Variable
		TO_EMAIL="stackcloud11@mkitconsulting.net"
		SUBJECT="File Successfully Copied Ola"
		BODY="The file {} was succesfully copied"
		FROM="oracle@MKIT-DEV-OEM.localdomain"

		# Calling the email function
		t.STACK_EMAIL(TO_EMAIL, SUBJECT, BODY, FROM)
	

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



# Main body

if __name__=="__main__":

	function = sys.argv[1]
	
	# Checking if the called function is database backup
	if function == "database_backup":
		
		# Variable declaration
		schema="stack_temp"
		runner="Olamide"
		directory="DATA_PUMP_DIR"

		# Calling the database backup function
		database_backup(schema, runner, directory) 

	# Checking if the called function is the file or diretory copy
	elif function == "copy":
		
		# Variable declaration
		f_d_to_copy="/home/oracle/scripts/practicedir_ola_sep23/olamide_training"
		dest_path="/home/oracle/scripts/practicedir_ola_sep23/backup/olamide_training"

		# Calling the directory copy function
		f_d_copy(f_d_to_copy, dest_path)
	
	else:
		print("Function Unknown")
