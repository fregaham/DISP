# Soubor main.py:

from disp.application import *
from disp.form import *
from disp.db import *
from disp.cursor import *
from disp.xmlui import *
from disp.file import *
from dbschema import *

class Main (Application):
  def initialize (self):

    self.title = "Address Book"

    form = Form (self)

    uiloader = XMLUIBuilder ()
    uiloader.loadFile ('form.xml', self, form)

    self.table.cursor = SOCursor (Person, orderBy = 'lastname')

    # Aktualne zvolena osoba v tabulce.
    self.person_id = None

    self.file_output = FileOutput (self,
      func = self.export,
      content_type = 'text/xml',
      filename = 'output.xml')

    form.open ()

  def onUpdate (self):
    if self.person_id:
      person = Person.get (self.person_id)
      person.set (
        firstname = self.edit_firstname.text,
        lastname = self.edit_lastname.text,
        email = self.edit_email.text)

      self.table.update ()

  def onNew (self):
    person = Person (
      firstname = self.edit_firstname.text,
      lastname = self.edit_lastname.text,
      email = self.edit_email.text)

    self.person_id = person.id
    self.table.update ()

  def onDelete (self):
    if self.person_id:
      Person.delete (self.person_id)
      self.table.update ()

  def onPersonSelected (self, person):
    self.edit_firstname.text = person.firstname
    self.edit_lastname.text = person.lastname
    self.edit_email.text = person.email

    self.person_id = person.id

  def onExport (self):
    self.file_output.open ()

  def export (self, stream):
    stream.write('<people>')
    self.table.cursor.begin ()
    for person in self.table.cursor:
      stream.write('<person>')
      stream.write('<firstname>%s</firstname>' % person.firstname)
      stream.write('<lastname>%s</lastname>' % person.lastname)
      stream.write('<email>%s</email>' % person.email)
      stream.write('</person>')

    self.table.cursor.end ()

    stream.write('</people>')

  def onFilter (self):
    filtr = self.edit_filter.text
    if filtr == '':
      self.table.cursor = SOCursor (Person, orderBy = 'lastname')
    else:
      self.table.cursor = SOCursor (Person, orderBy = 'lastname',
        clause = OR(
          LIKE(Person.q.lastname, filtr),
          LIKE(Person.q.firstname, filtr)))
    self.table.update ()
