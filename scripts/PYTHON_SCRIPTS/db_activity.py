#!/usr/bin/python


import cx_Oracle

# Variable declaration
OP_ID=1
OP_NAME='Datbase_Migration'

connection = cx_Oracle.connect(user = "STACK_OLA_SEP23", password="stackinc", dsn = "MKIT-DEV-OEM/APEXDB")
print(connection.version)


cursor=connection.cursor()
cursor.execute("""insert into operations values(:OP_ID_INS,:OP_NAME_INS)""",
OP_ID_INS=OP_ID,
OP_NAME_INS=OP_NAME)

connection.commit()
