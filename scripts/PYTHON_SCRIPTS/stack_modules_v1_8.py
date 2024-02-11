#!/usr/bin/bash

# Import Modules
import time,os,shutil,sys,gzip



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
		running_command=subprocess.run(["/bin/bash", export_command_file_fullpath])

	except:
	
		print("Database backup failed")


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

	except:
		print("Copy command failed")


def disk_maintenance_check_on_prem(disk_path, threshold):
	
	try:

		# printing the disk we are checking to standard output
		print("Checking disk usage for {}".format(disk_path))

		# Assigning a variable to the disk utilization function
		
		disk_space=shutil.disk_usage(disk_path)

		# Printing the disk space to standard output
		print("The current usage for {} is {}".format(disk_path, disk_space))
 
		# Checking if disk utilization is above threshold

		if disk_space > threshold:
			
			# printing a message to standard output if disk utilization is above threshold
			print("Disk utilization is above threshold!")

		else:
			print("")

	except:
		print("Disk utilization check failed")

def G_Zipp(file_to_zip):

	try:
		# Variable declaration
		stamped_zipped_file="{}_{}.gz".format(file_to_zip, TS)
			
		# Stating the file to Zip up
		print("Zipping up {}".format(file_to_zip))
	
		# Opening the file to be zipped in read binary mode
		zip_in = open(file_to_zip, "rb")
	
		# Creating a zip file in write binary mode
		zip_out = gzip.open(stamped_zipped_file, "wb")

		# Copying content of the unzipped file to the zipped file
		shutil.copyfileobj(zip_in, zip_out)

		# Stating the zip file created
		print("{} has been successfully created".format(stamped_zipped_file))

	except:
		print("Gzip failed")



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
