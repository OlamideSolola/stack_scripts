#!/usr/bin/python
#module import
import sys 


def myfirstfunction(a,b,c):
	print("My name is %s, %s, %s " %(a,b,c))

if __name__=="__main__":
	x,y,z=sys.argv[1], sys.argv[2], sys.argv[3]

	myfirstfunction(x,y,z)



