#!/usr/bin/python


import sys
import credit_check as c



if __name__ == "__main__":
	
	# Variable declaration	
	SSN=sys.argv[1]
	
	#Calling the credit_card function
	c.credit_check(args1=SSN)

