# Soubor dbschema.py:

from sqlobject import *

sqlhub.processConnection = connectionForURI('mysql://is:is@127.0.0.1/is2?cache=')

class Person(SQLObject):
  firstname = StringCol()
  lastname = StringCol()
  email = StringCol()

if __name__ == '__main__': 
  Person.createTable()
