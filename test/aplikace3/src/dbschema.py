
import sqlobject

class Person(sqlobject.SQLObject):
	name = sqlobject.UnicodeCol()
	position = sqlobject.UnicodeCol()
	bla = sqlobject.BoolCol()
	emails = sqlobject.MultipleJoin('Email')
	
class Email(sqlobject.SQLObject):
	email = sqlobject.UnicodeCol()
	person = sqlobject.ForeignKey('Person')

if __name__ == '__main__':
	sqlobject.sqlhub.processConnection = sqlobject.connectionForURI('mysql://is:is@127.0.0.1/is')
	Person.createTable()
	Email.createTable()
