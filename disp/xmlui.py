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

#import libxml2

import xml.parsers.expat
import form
import os
import pobject

class ParserHandler:
	
	def __init__ (self, handler, root, types):
		self.handler = handler
		self.types = types
		self.stack = []
		self.push (root)
		
	def push (self, obj):
		self.stack.append (obj)
		
	def pop (self):
		return self.stack.pop ()
	
	def top (self):
		return self.stack[-1]
	
	def startElement(self, tag, attrs):
		if tag in self.types:
			
			#print "startElement: %s, %s" % (tag, repr(attrs))
			
			# Rodic, ke tkeremu zavesime tento element
			parent = self.top ()
			
			_id = None
			args = None
			if attrs != None:
				args = {}
				
				for name, value in attrs.items ():
					# id oznacuje atribut pod jakym se ma objevit v objektu 'obj'
					if name == "id":
						_id = str(value)
					else:
						args[str(name)] = str(value)
			
			# atributy pouzijeme jako argumenty konstruktoru
			if args:
				newobj = self.types[tag] (parent, **args)
			else:
				newobj = self.types[tag] (parent)
			
			# a priradime objekt podle "id"
			if _id != None:
				setattr (self.handler, _id, newobj)
				
			self.push (newobj)
			
		elif tag == "handler":
			# handler ma povinne atributy, event a handler
			# event je nazev udalosti, handler je nazev obsluzne metody objektu "obj"
			event_name = attrs["event"]
			handler_name = attrs["handler"]
			
			event_obj = self.top ()
			event = getattr (event_obj, event_name)
			
			handler = getattr (self.handler, handler_name)
			
			event.addHandler (handler)
	
	def endElement(self, tag):
		if tag in self.types:
			self.pop ()

class XMLUIBuilder:
	def __init__ (self):
		
		self.types = {}
		
		self.addType ("Form", form.Form)
		self.addType ("Table", form.Table)
		self.addType ("TableColumn", form.TableColumn)
		self.addType ("Button", form.Button)
		self.addType ("LineEdit", form.LineEdit)
		self.addType ("StaticText", form.StaticText)
		self.addType ("VBox", form.VBox)
		self.addType ("HBox", form.HBox)
		self.addType ("VButtonBox", form.VButtonBox)
		self.addType ("HButtonBox", form.HButtonBox)
		self.addType ("VPane", form.VPane)
		self.addType ("HPane", form.HPane)
		self.addType ("Grid", form.Grid)
		self.addType ("TabBox", form.TabBox)
		self.addType ("Tab", form.Tab)
		self.addType ("Spacer", form.Spacer)
		self.addType ("CheckBox", form.CheckBox)
		self.addType ("RadioBox", form.RadioBox)
		self.addType ("FrameBox", form.FrameBox)
		
	def addType (self, name, ctor):
		self.types[name] = ctor
	
	def loadFile (self, filename, handler_object, root):
		handler = ParserHandler(handler_object, root, self.types)
		
		parser = xml.parsers.expat.ParserCreate()
		parser.StartElementHandler = handler.startElement
		parser.EndElementHandler = handler.endElement
		
		f = file (handler_object._root.absolutePath(filename), "rb")
		parser.ParseFile (f)
		f.close ()
		
		#parser = libxml2.createPushParser(handler, "", 0, filename)
		#fin = file(handler_object._root.absolutePath(filename), 'rb')
		#for line in fin:
			#parser.parseChunk(line, len(line), 0)
		#fin.close()
		#parser.parseChunk("", 0, 1)

__all__ = ["XMLUIBuilder"]
