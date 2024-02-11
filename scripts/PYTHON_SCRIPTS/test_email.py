#!/usr/bin/python


# Variables
TO_EMAIL='stackcloud11@mkitconsulting.net'
SUBJECT='Test Email Ola'
BODY="This is a test email"
FROM='oracle@MKIT-DEV-OEM.localdomain'

MSG=("\n".join(("FROM: %s" %FROM, "To: %s" %TO_Email, "Subject: %s:\n" %SUBJECT, "%s" %BODY)))

with smtplib.SMTP('localhost') as my_server:
	my_server.sendmail(FROM, TO_EMAIL, MSG)
	print("Email sent successfully to %s" %TO_EMAIL)
