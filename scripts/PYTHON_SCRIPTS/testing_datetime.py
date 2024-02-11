#!/usr/bin/python



import datetime




current_date_time = datetime.datetime.now()
date_time_formated=current_date_time.strftime("%d-%b-%Y %H:%M:%S")
print(date_time_formated)
