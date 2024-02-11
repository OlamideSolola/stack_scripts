#!/usr/bin/python

import time, os

# Variable declaration
timestring = time.localtime()
TS = time.strftime("%d%m%Y%H%M%S", timestring)
print(TS)
backup_base="/backup/AWSSEP23/APEXDB"
runner="OLAMIDE"
backup_dir=os.path.join(backup_base,runner)


try:

	fo = open("export_stack_temp.par_{}".format(TS), "w+")
	fo.write("userdid='/ as sysdba'\nschemas=stack_temp\ndumpfile=stack_temp_Olamide_.dmp_{}\nlogfile=stack_temp_Olamide_.log_{}\ndirectory=DATA_PUMP_DIR".format(TS,TS))
	fo.close()

	fo = open("export_stack_temp.par", "r+")
	file_content = fo.read()
	print(file_content)
	fo.close()
	file_path="/home/oracle/scripts/practicedir_ola_sep23/export_stack_temp.par_{}".format(TS)

	if os.path.isfile(file_path):
		print("Par file exists")
	backup_path=os.path.join(backup_dir,TS)
	os.mkdir(backup_path)
	if os.path.isdir(backup_path):
		print("Timestamped backup path exists")
except:
	print("fo failed")
