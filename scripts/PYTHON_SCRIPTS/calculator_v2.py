#!/usr/bin/python


# Module Declaration
import stack_modules_v2.py 

x = 20
y = 10
	
# Function Definition
def calculator(a, b):
	g=stack_modules_v2.py.add_func(x, y)
	print(g)


if __name__=="__main__":
	calculator(x, y)
