# -*- coding: utf-8 -*-
# copyright (C) 2006 Marek Schmidt

# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

from disp.application import *
from disp.form import *
from disp.file import *
from disp.cursor import *
from disp.db import *
from disp.xmlui import *

import sqlobject
import types

from dbschema import *


	
class AddEmailForm (Form):
	def __init__ (self, parent):
		Form.__init__ (self, parent)
		
		#uiloader = XMLUIBuilder ()
		#uiloader.loadFile ("add_email_form.xml", self, self)
		
		vbox = VBox (self)
		hbox = HBox (vbox)
		StaticText (hbox, text="Email here:")
		
		self.edit_email = LineEdit (hbox)
		
		hbox = HBox (vbox)
		self.ok = Button (hbox, text="OK")
		self.cancel = Button (hbox, text="Cancel")
		
		self.ok.clicked.addHandler (self.onOK)
		self.cancel.clicked.addHandler (self.onCancel)
		
	def onOK (self):
		self.close (True)
		
	def onCancel (self):
		self.close (False)
	
class MyForm (Form):
	def __init__ (self, parent):
		
		Form.__init__ (self, parent)
		
		self.initDB ()
		
		uiloader = XMLUIBuilder ()
		uiloader.loadFile ("myform.xml", self, self)
		
		# nastavime data do tabulek:
		self.table.cursor = SOCursor (self.Person, orderBy="name")
		
		self.file_output = FileOutput (self, func=self.export, content_type="text/xml", filename="output.xml")
		
		self.file_input = FileInput (self, func=self._import)
		
		self.add_email_form = AddEmailForm (self._parent)
		self.add_email_form.closed.addHandler (self.onAddEmailClosed)
		
		self.edit_id = None
		
	def initDB (self):
		self.db = SOConnection(self, "mysql://is:is@127.0.0.1/is?cache=")
		self.Person = SOClass(self.db, Person)
		self.Email = SOClass(self.db, Email)
	
	def _import (self, stream):
		
		text = ""
		while True:
			chunk = stream.read ()
			if not chunk: break
			text += chunk
			
		self.static.text = text.decode("utf8")
		
	def export (self, stream):
		
		output = "<doc>"
		output += "<name>%s</name>\n" % self.edit_name.text
		output += "<position>%s</position>\n" % self.edit_position.text
		output += "</doc>"
		
		stream.write (output.encode ("utf8"))
		
		
	def onEmailSelected (self, line):
		self.static.text = "onEmailSelected: %s\n" % str(line)
		
	def onAddEmail (self):
		if self.edit_id != None:
			# Zobrazime dialog na pridani emailu
			self.add_email_form.open ()
			
	def onAddEmailClosed (self, status):
		if status == True:
			# stisknuto OK:
			
			if self.edit_id:
				# vlozime do databaze novy email
				email = self.Email(email = self.add_email_form.edit_email.text, person=self.edit_id)
				
				self.table_emails.update ()
	
	def onDeleteEmail (self):
		
		self.static.text += "line != None, onDeleteEmail"
		
		line = self.table_emails.getSelectedLine ()
		if line != None:
			self.Email.delete (line.id)
			self.table_emails.update ()
		
	def onExport (self):
		self.file_output.open ()
		
	def onImport (self):
		self.file_input.open ()
		
	def onUpdate (self):
		
		p = self.Person.get (self.edit_id)
		p.set (name=self.edit_name.text, position=self.edit_position.text, bla=self.check_bla.checked)
		
		self.table.update ()
		
	def onNew (self):
		p = self.Person(name=self.edit_name.text, position=self.edit_position.text, bla=self.check_bla.checked)
		self.table.update ()
		
	def onDelete (self):
		self.Person.delete (self.edit_id)
		self.table.update ()
		
	def onPersonSelected (self, person):
		self.static.text = str(person)
		
		self.edit_id = person.id
		self.edit_name.text = person.name
		self.edit_position.text = person.position
		self.check_bla.checked = person.bla
		
		self.table_emails.cursor = SOCursor (self.Email, clause=Email.q.personID==person.id)
		
	def onButtonButton (self):
		button = Button (self.form2_vbox, text="Hello")
		button.clicked.addHandler (self.onButtonButton)
		
	def onButtonHideClicked (self):
		if self.form2_vbox.visible:
			self.form2_vbox.hide ()
			self.button_hide.text = "Show"
		else:
			self.form2_vbox.show ()
			self.button_hide.text = "Hide"

class Main (Application):
	def initialize (self):
		self.title = "Hola hej!"
		form = MyForm (self)
		form.open ()
		