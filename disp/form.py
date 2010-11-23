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
from event import Event

class ComponentBase:
	def __init__(self, parent = None):
		pass

	def show (self):
		pass

	def hide (self):
		pass

class ContainerBase(ComponentBase):
	def __init__ (self, parent = None):
		pass

	def append (self, component):
		""" Vloží komponentu do kontejneru. Neměla by se volat přímo. Vždy jen z konstruktorů na rodiče.
		"""
		pass
		
	def remove (self, component):
		pass
		
	def clear (self):
		pass

class FormBase(ContainerBase):
	def __init__(self, parent = None):
		pass
		
	def getEventOpened (self):
		pass
	
	def getEventClosed (self):
		pass
	
	opened = property(fget=lambda self: self.getEventOpened())
	closed = property(fget=lambda self: self.getEventClosed())
		

class TableBase(ComponentBase):
	
	def __init__(self, parent = None, rows=20):
		pass
		
	def getEventLineSelected (self):
		pass
	
	def getSelectedLine (self):
		pass

	def setCursor (self, cursor):
		pass

	def getCursor (self):
		pass
	
	cursor = property(fget=lambda self: self.getCursor(), fset=lambda self, v: self.setCursor(v))
	
	lineSelected = property(fget=lambda self: self.getEventLineSelected())
	
	def addColumn (self, column):
		pass
		
	def update (self):
		pass
	
class TableColumnBase(ComponentBase):
	def __init__ (self, parent = None, column = None, label = None):
		pass
		
	def render (self, obj):
		pass
	


class ButtonBase(ComponentBase):
	
	def __init__(self, parent = None, text=""):
		pass
		
	def getEventClicked (self):
		pass

	def setText (self, text):
		pass

	def getText (self):
		pass
	
	text = property(fget=lambda self: self.getText(), fset=lambda self, v: self.setText(v))
	clicked = property(fget=lambda self: self.getEventClicked())

class LineEditBase(ComponentBase):
	
	def __init__(self, parent = None, text="", size = None):
		pass

	def setText (self, text):
		pass

	def getText (self):
		pass
	
	text = property(fget=lambda self: self.getText(), fset=lambda self, v: self.setText(v))

class StaticTextBase(ComponentBase):
	def __init__(self, parent = None, text = ""):
		pass

	def setText (self, text):
		pass
		
	def getText (self):
		pass

	text = property(fget=lambda self: self.getText(), fset=lambda self, v: self.setText(v))

class VBoxBase(ContainerBase):
	def __init__ (self, parent = None):
		pass

class HBoxBase(ContainerBase):
	def __init__ (self, parent = None):
		pass
	
class VButtonBoxBase(ContainerBase):
	def __init__ (self, parent = None):
		pass

class HButtonBoxBase(ContainerBase):
	def __init__ (self, parent = None):
		pass
	
class VPaneBase(ContainerBase):
	def __init__ (self, parent = None):
		pass
	
class HPaneBase(ContainerBase):
	def __init__ (self, parent = None):
		pass

class GridBase(ContainerBase):
	def __init__ (self, parent = None, rows=0, cols=0):
		pass
	
class TabBoxBase(ComponentBase):
	def __init__ (self, parent = None):
		pass
	
class TabBase(ContainerBase):
	def __init__ (self, parent = None, label = ""):
		pass
	
	def setLabel (self, label):
		pass

	def getLabel (self):
		pass
	
	label = property(fget=lambda self: self.getLabel(), fset=lambda self, v: self.setLabel(v))
	
class SpacerBase (ComponentBase):
	def __init__ (self, parent = None):
		pass
	
class CheckBoxBase(ComponentBase):
	def __init__ (self, parent = None, text = "", checked = False):
		pass
		
	def setText (self, text):
		pass

	def getText (self):
		pass
	
	def setChecked (self, checked):
		pass
		
	def getChecked (self):
		pass

	text = property(fget=lambda self: self.getText(), fset=lambda self, v: self.setText(v))
	checked = property(fget=lambda self: self.getChecked(), fset=lambda self, v: self.setChecked(v))

class RadioBoxBase(ComponentBase):
	def __init__(self, parent = None, option = None):
		pass
	
	def setOption (self, option):
		pass
	
	def getOption (self):
		pass
	
	def addOption (self, option):
		pass
	
	def removeOption (self, option):
		pass
		
	option = property(fget=lambda self: self.getOption(), fset=lambda self, v: self.setOption(v))

class FrameBoxBase(ComponentBase):
	def __init__ (self, parent = None, label = ""):
		pass
	
	def setLabel (self, label):
		pass
	
	def getLabel (self):
		pass
	
	label = property(fget=lambda self: self.getLabel(), fset=lambda self, v: self.setLabel(v))
