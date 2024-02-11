#!/usr/bin/python


def test_dictionaries():
	servers={
    "Hosts":[{"MKIT-DEV-OEM":"ON-PREM"},{"STACKCLOUD":"CLOUD"}],
    "Disks":["/u01","/u02","/u03","/u04","/u05","/backup"],
    "Transient_directory_paths":[{"/u01":"/u01/app/oracle/admin/APEXDB/adump"},{"/backup":"/backup/AWSJUL22/RAMSEY/FILE"}]
    }

	print(servers)



	




"""

x = 10
y = 5


def add_func(a, b):
	z = x + y
	print(z)

def sub_func(a, b):
	z = x - y
	print(z)

def mul_func(a, b):
	z = x * y
	print(z)



if __name__=="__main__":
	add_func(x, y)
	sub_func(x, y)
	mul_func(x, y)	 
"""


	test_dictionaries()
