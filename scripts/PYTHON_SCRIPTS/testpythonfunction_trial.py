#!/usr/bin/python

#module import
import sys

def myfirstfunction(a,b,c):
	print("The values entered into the module are %s %s %s"%(a,b,c))
	if int(a)>6:
		print("%s is greater than 6"%(a))

if __name__=="__main__":
	x,y,z=sys.argv[1],sys.argv[2],sys.argv[3]
	count_args=len(sys.argv) - 1
	print("The number of command line argument is %s" %(count_args))
	myfirstfunction(x,y,z)

