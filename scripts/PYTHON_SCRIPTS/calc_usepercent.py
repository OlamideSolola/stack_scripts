#!/usr/bin/python


# Module Import
import shutil
import sys



# Variable Declaration

disk_path="/u01"

disk_space=shutil.disk_usage(disk_path)
print(disk_space)
Total_disk_space=disk_space[0]
print("The total disk space is {}".format(Total_disk_space))

Used_disk_space=disk_space[1]
print("The used disk space is {}".format(Used_disk_space))

free_disk_space=disk_space[2]
print("The free disk space is {}".format(free_disk_space))

use_percent =(Used_disk_space/Total_disk_space)* 100
print("The use percent is {}".format(use_percent))


threshold=20

if use_percent > threshold:
	print("The use percent is greater than threshold! ")

