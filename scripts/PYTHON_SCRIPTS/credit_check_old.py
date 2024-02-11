#!/usr/bin/python

import cx_Oracle as c

import sys


def credit_check(**args):
	# Connecting into the database with our connection details
	connection=c.connect(user="STACK_OLA_SEP23", password="stackinc", dsn="MKIT-DEV-OEM/APEXDB")

	# Defining the cursor
	cursor=connection.cursor()

	# Reading the SSN from the credit_check table
	cursor.execute("""select CREDIT_SCORE from credit_check where SSN = :SSN""",
	SSN=args['args1'])
	
	fetched_credit_score = cursor.fetchone()
	
	return fetched_credit_score

if __name__ == "__main__":


	# Variable declaration
	SSN=sys.argv[1]

	#Calling the credit_card function
	credit_score_result = credit_check(args1=SSN)
	
	for credit_score in credit_score_result:

		#Checking if the credit card is approved
		if credit_score > 720:
			print("Approved")

		else:
			print("Not Approved")
	
