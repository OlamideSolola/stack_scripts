#!/usr/bin/bash

# Import Modules
import time,os,shutil,sys,gzip,smtplib,subprocess



# Variable declaration
timestring=time.localtime()
TS=time.strftime("%m%d%Y%H%M%S", timestring)


# Function definition

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

	print(par_file_fullpath)
	
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
		
		# Variable declaration to Send Email for a succesful backup
		TO_EMAIL="stackcloud11@mkitconsulting.net"
		SUBJECT="Successfull Database Backup Ola"
		BODY="The schema " + args["args1"] +  " was succesfully exported"
		FROM="oracle@MKIT-DEV-OEM.localdomain"

		# Calling the email function
		STACK_EMAIL(TO_EMAIL, SUBJECT, BODY, FROM)
							
		
	except:
	
		print("Database backup failed")


		# Variable declaration to Send Email for a succesful backup
		TO_EMAIL="stackcloud11@mkitconsulting.net"
		SUBJECT="Database Backup failed Ola"
		BODY="The schema " + args["args1"] +  " was not exported"
		FROM="oracle@MKIT-DEV-OEM.localdomain"

		# Calling the email function
		#STACK_EMAIL(TO_EMAIL, SUBJECT, BODY, FROM)
		

def f_d_copy(**args):

	
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

		# Variable declaration to Send Email for a succesful copy
		TO_EMAIL="stackcloud11@mkitconsulting.net"
		SUBJECT="Successful file or directory copy Ola"
		BODY="The file or directory {} was successfully copied to {}".format(args["args1"], args["args2"])
		FROM="oracle@MKIT-DEV-OEM.localdomain"

		# Calling the email function
		STACK_EMAIL(TO_EMAIL, SUBJECT, BODY, FROM)		

	except:
		print("Copy command failed")

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

		if use_percent > int(args["args2"]):
			
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
	imp_parfile_name="impdp_" + args["args1"] + "_stack_" + args["args4"] + ".par"
	imp_parfile_path=os.path.join(file_base_path, imp_parfile_name)
	user="'/ as sysdba'"
	migrated_schema=args["args1"] + ":stack_" + args["args4"] + "_migrated"
	logfile=args["args1"] + "_" + args["args4"] + "_" + TS + ".log"
	import_command_file="import.sh"
	imp_command_fullpath=os.path.join(file_base_path, import_command_file)
	exp_backup_path="/backup/AWSSEP23/APEXDB"
	imp_backup_path="/backup/AWSSEP23/SAMD/"
	exp_dumpfile_fullpath=os.path.join(exp_backup_path, args["args2"])
	imp_dumpfile_fullpath=os.path.join(imp_backup_path, args["args2"] )
	dmp_basename=os.path.basename(args["args2"])
	print(dmp_basename)	
	
	try:
		
		# Printing the full path to the provided dumpfile
		#print("The fullpath of the gziped dmp file is {}".format(exp_dumpfile_fullpath))
	
		# Calling the unzip gzip function to un zip the dumpfile
		new_dumpfile=unzip_gzipp(args1="/backup/AWSSEP23/APEXDB/stack_temp_Olamide_01202024081335.dmp_01202024091436.gz")
		print("{}".format(new_dumpfile))	
		
		# Removing the extention from the zipped dumpfile
		new_dumpfile_name=os.path.splitext(dmp_basename)[0]
			
		# Creating the fullpath of the unzipped dumpfile and printing the path 
		new_dumpfile_fullpath=os.path.join(exp_backup_path, new_dumpfile_name)
		print("The fullpath of the unziped dmp file is {}".format(new_dumpfile_fullpath))

		# Copying the unzipped dmp file to the physical path of the database import location
		shutil.copy(new_dumpfile_fullpath, imp_backup_path)		

		# Creating and printing fullpath of the copied dmp file 
		imp_dumpfile_fullpath=os.path.join(imp_backup_path, new_dumpfile_name)

		# Checking the file exist in the import location
		if imp_dumpfile_fullpath:
			print("The unzipped dumpfile was successfully of the copied to the import location. Fullpath: {}".format(imp_dumpfile_fullpath))
		
		# Creating the import parfile in write and read mode
		im=open(imp_parfile_path, "w+") 

		# Writing into the import parameter file
		im.write("userid=" + user + "\nschemas=" + args["args1"] + "\nremap_schema=" + migrated_schema + "\ndumpfile=" + new_dumpfile_name  + "\nlogfile=" + logfile + "\ndirectory=" + args["args3"] + "\ntable_exists_action=replace")
		
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
	

		# Variable declaration for sending a mail
		TO_EMAIL="stackcloud11@mkitconsulting.net"
		SUBJECT="Database Import successfully completed Ola"
		BODY="The dumpfile " + new_dumpfile_name + " was successfully imported"
		FROM="oracle@MKIT-DEV-OEM.localdomain"

		# Calling the email function
		t.STACK_EMAIL(TO_EMAIL, SUBJECT, BODY, FROM)

	
	except:
		print("Database import failed")

		# Variable declaration for sending a mail
		TO_EMAIL="stackcloud11@mkitconsulting.net"
		SUBJECT="File Successfully Copied Ola"
		BODY="The file {} was succesfully copied"
		FROM="oracle@MKIT-DEV-OEM.localdomain"

		# Calling the email function
		#t.STACK_EMAIL(TO_EMAIL, SUBJECT, BODY, FROM)
	


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
