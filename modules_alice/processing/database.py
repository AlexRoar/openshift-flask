import mysql.connector

mydb = mysql.connector.connect(
  host='http://dialogs-db-allice.7e14.starter-us-west-2.openshiftapps.com',
  user="dialogs",
  passwd="YouKnowNothing"
)


print(mydb)
