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

import types

import disp
import disp.pobject
import disp.form
import disp.event
import disp.session

from mod_python import apache

class ComponentXul (disp.form.ComponentBase, disp.pobject.PObject):
	def __init__(self, parent=None):
		disp.pobject.PObject.__init__ (self, parent)
		self.visible = True
		
		if parent != None:
			parent.append (self)
		
	def show (self):
		self.visible = True
		self.xul_client_call ("show", None)
		
	def hide (self):
		self.visible = False
		self.xul_client_call ("hide", None)
	
	def xul_call (self, fname, args):
		pass
	
	def xul_state (self, state):
		pass
	
	def xul_client_create (self, xul_class):
		self._root.xul_client_create (xul_class, self._id)
	
	def xul_client_call (self, fname, args):
		self._root.xul_client_call (self._id, fname, args)

disp.form.Component = ComponentXul

class ContainerXul (ComponentXul, disp.form.ContainerBase):
	def __init__ (self, parent=None):
		ComponentXul.__init__ (self, parent)
		
	def append (self, component):
		self.xul_client_call ("add", component._id)
		
	def remove (self, component):
		self.xul_client_call ("remove", component._id)
		
disp.form.Container = ContainerXul

class FormXul (ContainerXul, disp.form.FormBase):
	def __init__(self, parent=None):
		ContainerXul.__init__ (self, parent)
		self.xul_client_create ("Form")
		
		self.event_opened = disp.event.Event (self)
		self.event_closed = disp.event.Event (self)
		
	def getEventOpened (self):
		return self.event_opened
	
	def getEventClosed (self):
		return self.event_closed
	
	def open (self):
		self._root.pushForm (self)
		self.event_opened ()
		
	def close (self, status=None):
		self._root.popForm (self)
		self.event_closed (status)

disp.form.Form = FormXul

class TableXul(ComponentXul, disp.form.TableBase):
	def __init__(self, parent=None, rows=20):
		ComponentXul.__init__ (self, parent)
		self.xul_client_create ("Table")
		self.xul_client_call ("set_rows", int(rows))
		
		self._cursor = None
		self._columns = []
		
		self.event_line_selected = disp.event.Event (self)
		
		self.selectedLine = None
		
	def getEventLineSelected (self):
		return self.event_line_selected
		
	def append (self, column):
		self._columns.append (column._name)
		self.xul_client_call ("add_column", column.label)
		
	def setCursor (self, cursor):
		self._cursor = cursor
		self.update ()
		
	def getCursor (self):
		return self._cursor
		
	def getSelectedLine (self):
		
		cursor = self.cursor
		
		if cursor != None and self.selectedLine != None:
			cursor.begin ()
			line = cursor[self.selectedLine]
			cursor.end ()
			
			return line
		
		return None
		
	def update (self):
		
		self.selectedLine = None
		
		msg = []
		
		cursor = self._cursor
		if cursor != None:
			cursor.begin ()
			
			for line in cursor:
				
				data = []
				for column in self._columns:
					column = self._children[column]
					data.append (column.render(line))
					
				msg.append (data)

			cursor.end ()
			
		self.xul_client_call ("update", msg)
		
		
	def xul_call (self, fname, args):
		if fname == "on_select":
			cursor = self._cursor
			
			if cursor != None:
				cursor.begin ()
				
				self.selectedLine = int(args)
				
				try:
					line = cursor[int(args)]
				except IndexError:
					# ignorujeme, pravdepodobne vybiral radek co neexistuje
					line = None
				
				if line != None:
					self.event_line_selected.call (line)
				
				cursor.end ()
		
disp.form.Table = TableXul

class TableColumnXul (ComponentXul, disp.form.TableColumnBase):
	def __init__ (self, parent = None, column = None, label = None):
		
		self.col = column
		self.label = label
		
		ComponentXul.__init__ (self, parent)
	
	def render (self, obj):
		if isinstance(obj, dict):
			return unicode (obj[self.col])
		else:
			return unicode (getattr(obj, self.col))

disp.form.TableColumn = TableColumnXul

class ButtonXul (ComponentXul, disp.form.ButtonBase):
	def __init__(self, parent=None, text=""):
		ComponentXul.__init__ (self, parent)
		self.xul_client_create ("Button")
		self.xul_client_call ("set_text", text)
		
		self._text = text
		self.event_clicked = disp.event.Event (self)
		
	def getEventClicked (self):
		return self.event_clicked
		
	def setText (self, text):
		self._text = text
		self.xul_client_call ("set_text", self.text)

	def getText (self):
		return self._text
		
	def xul_call (self, fname, args):
		if fname == "on_command":
			self.event_clicked.call ()
		

disp.form.Button = ButtonXul


class LineEditXul (ComponentXul, disp.form.LineEditBase):
	def __init__(self, parent=None, text="", size=None):
		ComponentXul.__init__ (self, parent)
		self._text = text
		
		self.xul_client_create ("LineEdit")
		self.xul_client_call ("set_text", self._text)
		
		if size != None:
			size = int(size)
			
			self.xul_client_call ("set_size", size)
		
	def xul_state (self, state):
		self._text = state
		
	def setText (self, text):
		self._text = text
		self.xul_client_call ("set_text", self._text)
		
	def getText (self):
		return self._text
		
disp.form.LineEdit = LineEditXul

class StaticTextXul (ComponentXul, disp.form.StaticTextBase):
	def __init__(self, parent=None, text = ""):
		ComponentXul.__init__ (self, parent)
	
		self._text = text
		self.xul_client_create ("StaticText")
		self.xul_client_call ("set_text", self._text)
		
	def setText (self, text):
		self._text = text
		self.xul_client_call ("set_text", self._text)
		
	def getText (self):
		return self._text
		
disp.form.StaticText = StaticTextXul

class VBoxXul (ContainerXul, disp.form.VBoxBase):
	def __init__ (self, parent=None):
		ContainerXul.__init__ (self, parent)
		self.xul_client_create ("VBox")
		
disp.form.VBox = VBoxXul

class HBoxXul (ContainerXul, disp.form.HBoxBase):
	def __init__ (self, parent=None):
		ContainerXul.__init__ (self, parent)
		self.xul_client_create ("HBox")
		
disp.form.HBox = HBoxXul

class VPaneXul (ContainerXul, disp.form.VPaneBase):
	def __init__ (self, parent=None):
		ContainerXul.__init__ (self, parent)
		self.xul_client_create ("VPane")
		
disp.form.VPane = VPaneXul

class HPaneXul (ContainerXul, disp.form.HPaneBase):
	def __init__ (self, parent=None):
		ContainerXul.__init__ (self, parent)
		self.xul_client_create ("HPane")
		
disp.form.HPane = HPaneXul

class VButtonBoxXul (ContainerXul, disp.form.VButtonBoxBase):
	def __init__ (self, parent=None):
		ContainerXul.__init__ (self, parent)
		self.xul_client_create ("VButtonBox")
		
disp.form.VButtonBox = VButtonBoxXul

class HButtonBoxXul (ContainerXul, disp.form.HButtonBoxBase):
	def __init__ (self, parent=None):
		ContainerXul.__init__ (self, parent)
		self.xul_client_create ("HButtonBox")
		
disp.form.HButtonBox = HButtonBoxXul

class GridXul (ContainerXul, disp.form.GridBase):
	def __init__ (self, parent=None, rows=0, cols=0):
		ContainerXul.__init__ (self, parent)
		
		self.rows = int(rows)
		self.cols = int(cols)
		
		self.xul_client_create ("Grid")
		self.xul_client_call ("set_size", [self.rows, self.cols])
		
disp.form.Grid = GridXul

class TabBoxXul (ContainerXul, disp.form.TabBoxBase):
	def __init__ (self, parent=None):
		ContainerXul.__init__ (self, parent)
		self._tabs = []
		self.xul_client_create ("TabBox")
		
	#def addTab (self, component, label):
		
		#assert component._parent == self
		#self._tabs.append ( (component._name, label) )
		
		#self.xul_client_call ("add_tab", [component._id, label])
		
disp.form.TabBox = TabBoxXul

class TabXul (ContainerXul, disp.form.TabBoxBase):
	def __init__ (self, parent=None, label=""):
		ContainerXul.__init__ (self, parent)
		self._label = label
		self.xul_client_create ("Tab")
		self._parent.xul_client_call ("set_tab_label", [self._id, self._label])
		
	def getLabel (self):
		return self._label
	
	def setLabel (self, label):
		self._label = label
		self._parent.xul_client_call ("set_tab_label", [self._id, self._label])
		
disp.form.Tab = TabXul

class CheckBoxXul (ComponentXul, disp.form.CheckBoxBase):
	def __init__(self, parent=None, text="", checked = False):
		ComponentXul.__init__ (self, parent)
		
		self._text = text
		self._checked = checked
		
		self.xul_client_create ("CheckBox")
		self.xul_client_call ("set_text", self._text)
		self.xul_client_call ("set_checked", self._checked)
		
	def xul_state (self, state):
		self._checked = state
		
	def setText (self, text):
		self._text = text
		self.xul_client_call ("set_text", self._text)
		
	def getText (self):
		return self._text
		
	def setChecked (self, checked):
		self._checked = checked
		self.xul_client_call ("set_checked", self._checked)
		
	def getChecked (self):
		return self._checked
		
disp.form.CheckBox = CheckBoxXul

class SpacerXul (ComponentXul, disp.form.SpacerBase):
	def __init__(self, parent=None):
		ComponentXul.__init__ (self, parent)
		self.xul_client_create ("Spacer")
		
disp.form.Spacer = SpacerXul

class RadioBoxXul(ComponentXul, disp.form.RadioBoxBase):
	def __init__(self, parent = None, option = None):
		ComponentXul.__init__ (self, parent)
		
		#self._options = []
		self._option = option
		
		self.xul_client_create ("RadioBox")
	
	def setOption (self, option):
		self._option = option
		self.xul_client_call ("set_option", self._option)
	
	def getOption (self):
		return self._option
	
	def addOption (self, option):
		#self._options.append (option)
		self.xul_client_call ("add_option", option)
	
	def removeOption (self, option):
		#self._options.remove (option)
		self.xul_client_call ("remove_option", option)
		
	def xul_state (self, state):
		self._option = state
	
disp.form.RadioBox = RadioBoxXul


class FrameBoxXul (ContainerXul, disp.form.FrameBoxBase):
	def __init__ (self, parent=None, label = ""):
		ContainerXul.__init__ (self, parent)
		self.xul_client_create ("FrameBox")
		self.setLabel (label)
		
	def setLabel (self, label):
		self._label = label
		self.xul_client_call ("set_label", label)
		
	def getLabel (self):
		return self._label
		
disp.form.FrameBox = FrameBoxXul
