#!/usr/bin/python
import sys
import os
import subprocess

"""
name = "Olamide"
lenght_name=len(name)
print(" The length of my name is {}".format(lenght_name))



b="Olamide "
print(b.strip())



threshold="65%"
threshold_number=threshold.strip("%")
print(threshold_number)


if int(threshold_number)  > 75:
	print("Threshold is greater than 75")
else:
	print("Threshold is less than 75")


b="Olamide"
uppercase_name=b.upper()
lowercase_name=b.lower()

print("My {} in upper case is {}".format(b, uppercase_name))


a="Stack"
print(a.replace("S","c"))


threshold="65%"
thres_num=threshold.replace("%","")
print(thres_num)
if int(thres_num) > 75:
	print("The threshold is greater that 75")
else:
	print("The threshold is less that 75")




rep=open("Test_replace", "w+")

rep.write("Baseball")

rep.close()


rep=open("Test_replace", "r+")
rep_content=rep.read()

New_content=rep_content.replace(rep_content,"Basketbal")
print(New_content)

rep.close()




rep=open("Test_replace", "w+")
rep.write(New_content)
rep.close()


rep=open("Test_replace", "r+")
rep_content=rep.read()
print(New_content)
rep.close()







Fullname="Olamide,Solola"
tokens=Fullname.split(",")

print(tokens[1])




disks="/u01,/u02,/u03,/u04,/u05,/backup"

tokens=disks.split(",")
print(tokens)


if tokens[5].strip("/") == "backup":
	print("This is the backup directory")
else:
	print("This is not the backup directory")



txt="Stack IT training students stack up a lot of bread"
if "bread" in txt:
	print("bread exists in statement")


txt="Stack IT training students stack up a lot of bread"
txt_lowercase=txt.lower()

if "stack" in txt_lowercase:
	cnt=txt_lowercase.count("stack")
	print("Stack appears {} times".format(cnt))

# Arbituary arguments
def my_function(*names):
	print("The youngest child is" + names[2])

my_function ("John", "Jeff", "Rachel")


def add_func(*numbers):
	result=numbers[0] + numbers[1]
	print(result)

add_func(1, 2)



# Keywords args

def my_function(name3, name1, name2):
	print("My name is " + name1)

my_function(name1="Nick",name3="Jose",name2="Rachel")



def my_function(**names):
	print("Nicks last name is" + names["lname"] + " and Nick is " + str(names["Age"]))

my_function(fname="Nick",lname="Moran", Age=29)



def add_function(**num):
	result = num["num1"]+ num["num2"]
	print(result)


def sub_function(**num):
	result = num["num1"]-num["num2"]
	print(result)


def mul_function(**num):
	result = num["num1"]*num["num2"]
	print(result)




if __name__=="__main__":

	function=sys.argv[1]


if function == "add":
	add_function(num1=10, num2=20)

elif function == "sub":
	sub_function(num1=100, num2=20)

elif function == "mul":
	mul_function(num1=20, num2=20)

else:
	print("Function Unknown")



names=["Myles", "Mike", "Charles" "Yinka" "Nick" "Ola"]
names.insert(3, "Ola")
#names.remove("Charles")
names.pop()
names.pop(0)
print(names)

del names[0]

length=len(names)
print(length)
print("")
names.clear
print(names)



# Joining lists
names=["Myles", "Mike", "Charles", "Yinka", "Nick", "Ola"]
names2=["Wilson", "Uche", "Remi"]
#names3=names+names2

#print(names3)


for x in names2:
	names.append(x)
print(names)



names=list(("Myles", "Mike", "Charles", "Yinka", "Nick", "Ola"))
print(names)





numbers=[1,1,2,2,3,4,5,6,6,7,8,9,9,10]
duplicates=[]
count=len(numbers)


for x in numbers:
	if number.count(x) > 1:
		duplicates.append(x)
		print(duplicates)



numbers=[1,1,2,2,3,4,5,6,6,7,8,9,9,10]
dedup=set(numbers)
print(dedup)





cars={
	"Brand":"Honda",
	"Model":"Accord",
	"Year":2010
}

print(cars)

print(cars["Brand"])
print(cars.get)


cars={
   "Brand":"Honda",
   "Model":"Accord",
   "Year":2010

}
for x in cars:
	print(x)

# getting the values
for x in cars:
	print(cars[x])



# using values to get values

for x in cars.values():
	print (x)



# using items to get keys and values

for x,y in cars.items():
	print(x, "=>", y)


cars={
    "Brand":"Honda",
    "Model":"Accord",
    "Year":2010

 }

if "Brand" in cars:
	print("Yes brand exists in the car dictionary")

print(len(cars))



# Adding a new key value pair to a dictionary
cars["Tag"]="15ABQ"
print(cars)




# using pop to remove a specified key
cars.pop("Tag")
print(cars)


cars.pop("Tag")


# Removing item from 

cars={
     "Brand":"Honda",
     "Model":"Accord",
     "Year":2010

  }

del cars["Year"]
print(cars)

#del cars
#print(cars)

# Empting (clearing) the dictionary

cars.clear()
print(cars)




cars={
      "Brand":"Honda",
      "Model":"Accord",
      "Year":2010

   }


# Copying a dictionary
cars2=cars.copy()
print(cars2)

#Another way to copy a dict
cars=dict(cars)
print(cars)



car1={
		"Brand":"Honda",
		"Model":"Accord",
		"Year":2010
}

car2={
      "Brand":"Toyota",
      "Model":"Camry",
      "Year":2005
}
car3={
      "Brand":"Mercedes",
      "Model":"GLE",
      "Year":2010,
}

cars={
	"cars1":car1,
	"cars2":car2,
	"cars3":car3


print(cars["car1"])



i = 1
while i < 6:
	print(i)
	i += 1

counter = 1
while counter < 6:
	print(counter)
	if counter == 3:
		break
	counter += 1


counter=0
while counter <= 0:
	print(counter)
	if counter == 11:
		break
	counter += 1



# infinite while loop

emptylist = []

while 2 > 1:
	i = int(input("Input a number: "))
	emptylist.append(i)
	if i == 0:
		break
print(emptylist)

"""



while 2 > 1:
	file="/home/oracle/scripts/practicedir_ola_sep23/test_loop.txt"
	if os.path.isfile(file):
		print("File exists")
		file_exist=subprocess.getoutput("ls -l {}".format(file))
		print(file_exist)
		break
		
	else:
		print("Looking for file text_loops.txt")







