#!/usr/bin/python

import cx_Oracle as c
import json
import sys


def credit_check(**args):
	# Opening the JSON file
	fo = open("/home/oracle/scripts/practicedir_ola_sep23/credit_check_json.txt")
	
	#Loading the JSON document
	JSON_INFO = json.load(fo)
	
	# Extrating the value of the key customer so we can loop through the table
	DICT_INFO=JSON_INFO['Customer']
	
	# Creating an empty list to store the SSN numbers
	new_SSN_list = []

	# Looping through the customer table to get the SSN Numbers
	for info in DICT_INFO:
	
		new_SSN_list.append(info["SSN"])

	
	
	# Checking the SSN entered by the user is in the SSN list
	if args['arg1'] in new_SSN_list:
		SSN_to_use = args['arg1']
		print(SSN_to_use)

	# Checking if SSN is not in the list	
	if args['arg1'] not in new_SSN_list:	
		print("SSN not in the SSN list")	
		exit()

	# Connecting into the database with our connection details
	connection=c.connect(user="STACK_OLA_SEP23", password="stackinc", dsn="MKIT-DEV-OEM/APEXDB")

	# Defining the cursor
	cursor=connection.cursor()

	# Reading the SSN from the credit_check table
	cursor.execute("""select CREDIT_SCORE from credit_check where SSN = :SSN""",
	SSN = SSN_to_use)

	fetched_credit_score = cursor.fetchone()

	return fetched_credit_score
	




	
if __name__ == "__main__":


	# Variable declaration
	SSN_PROVIDED=sys.argv[1]

	#Calling the credit_card function
	credit_score_result = credit_check(arg1 = SSN_PROVIDED)
	
	for credit_score in credit_score_result: 
	#Checking if the credit card is approved
		if credit_score > 720:
			print("Approved")

		else:
			print("Not Approved")
	
