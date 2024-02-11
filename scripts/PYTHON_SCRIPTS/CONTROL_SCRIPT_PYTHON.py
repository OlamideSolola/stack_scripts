#!/usr/bin/python

#Module Declaration
import stack_modules as t


#Variable declaration 
hostname = "MKIT_DEV-OEM"


if __name__=="__main__":
	dict_output=t.get_server_dictionary()

	if	dict_output["Hosts"][0]["MKIT-DEV-OEM"] == "ON-PREM":
		print("This is an On prem server")
	else:
		print("This is a cloud server")
