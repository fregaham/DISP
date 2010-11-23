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
import disp.form
import disp.event

import gobject
import gtk

class ComponentGtk (disp.form.ComponentBase, disp.pobject.PObject):
	def __init__(self, parent=None, expand=True, fill=True, padding=4):
		
		disp.pobject.PObject.__init__ (self, parent)
		
		self.gtk_expand = expand
		self.gtk_fill = fill
		self.gtk_padding = padding
		
		self.gtk_expand = expand
		
		self.visible = True
		
		if parent != None:
			parent.append (self)
			
			if isinstance (parent, ComponentGtk):
				parent.gtk_set_child_packing (self, expand, fill, padding)
			
	def gtk_set_child_packing (self, child, expand=True, fill=True, padding=4):
		""" Metoda, kterou vola komponenta, ktera se potrebuje 'protahnout', 
		  napriklad Table. Musi se tak rekurzivne expandovat i vsechny kontejnery nad ni.
		"""
		pass
		
	
	def gtk_show (self):
		""" Rekurzivne zobrazi objekty """
		if self.visible:
			self.gtk_object.show_all ()
		else:
			self.gtk_object.hide ()
	
	def gtk_hide (self):
		""" Schova objekty """
		self.gtk_object.hide ()
		
	def show (self):
		self.visible = True
		self.gtk_show ()
		
	def hide (self):
		self.visible = False
		self.gtk_hide ()

disp.form.Component = ComponentGtk

class ContainerGtk (disp.form.ContainerBase, ComponentGtk):
	def __init__ (self, parent=None, expand=True, fill=True, padding=4):
		ComponentGtk.__init__ (self, parent, expand, fill, padding)
		
	#def append (self, component):
		#self.gtk_object.add (component.gtk_object)
		
	def remove (self, component):
		self.gtk_object.remove (component.gtk_object)
		
	def clear (self):
		#TODO
		pass
	
	def gtk_show (self):
		for i in self._children.values ():
			if hasattr(i, "gtk_show"):
				i.gtk_show ()
				
		if self.visible:
			self.gtk_object.show ()
		else:
			self.gtk_object.hide ()
		
	
	def gtk_hide (self):
		self.gtk_object.hide ()
		for i in self._children:
			if hasattr(i, "gtk_show"):
				i.gtk_hide ()
	
disp.form.Container = ContainerGtk

class FormGtk (ContainerGtk, disp.form.FormBase):
	def __init__(self, parent=None):
		self.gtk_object = gtk.VBox()
		ContainerGtk.__init__ (self, parent, False)
		
		self.event_opened = disp.event.Event (self)
		self.event_closed = disp.event.Event (self)
		
	def getEventOpened (self):
		return self.event_opened
	
	def getEventClosed (self):
		return self.event_closed
		
	def append (self, component):
		self.gtk_object.pack_start (component.gtk_object, expand=component.gtk_expand, padding=component.gtk_padding)
		
	def gtk_set_child_packing (self, child, expand=True, fill=True, padding=4):
		self.gtk_object.set_child_packing (child.gtk_object, expand, fill, padding, gtk.PACK_START)
		
		if self.gtk_expand == False and expand:
			self.gtk_expand = True
			
			if isinstance(self._parent, ComponentGtk):
				self._parent.gtk_set_child_packing (self)
			
		
	def open (self):
		self._root.pushForm (self)
		self.event_opened ()
		
	def close (self, status = None):
		self._root.popForm (self)
		self.event_closed (status)

disp.form.Form = FormGtk

class TableGtk(ComponentGtk, disp.form.TableBase):
	def __init__(self, parent=None, rows=20):
		
		self.gtk_object = gtk.ScrolledWindow ()
		self.gtk_treeview = gtk.TreeView ()
		self.gtk_model = None
		
		self.gtk_object.add (self.gtk_treeview)
		
		self.gtk_treeview.connect ("row-activated", self.gtk_on_row_activated)
		self.line_cache = {}
		
		self._cursor = None
		self._columns = []
		
		#self.gtk_treeview.set_size_request (-1, 20 * 20)
		
		self.selectedLine = None
		
		ComponentGtk.__init__ (self, parent, True)
		self.event_line_selected = disp.event.Event (self)
		
	def setCursor (self, cursor):
		self._cursor = cursor
		self.update ()
		
	def getCursor (self):
		return self._cursor
		
	def getEventLineSelected (self):
		return self.event_line_selected
	
	def getSelectedLine (self):
		return self.selectedLine
		
	def update (self):
		
		self.selectedLine = None
		
		args = []
		for column in self._columns:
			args.append (gobject.TYPE_STRING)
		
		self.gtk_model = gtk.ListStore (*args)
		
		self.line_cache = {}
		cursor = self._cursor
		if cursor != None:
			cursor.begin ()

			for line in cursor:
				
				data = []
				for column in self._columns:
					data.append (column.render (line))
									
				i = self.gtk_model.append (data)
				self.line_cache[self.gtk_model.get_string_from_iter (i)] = line

			cursor.end ()
		
		self.gtk_treeview.set_model (self.gtk_model)
	
	def append (self, column):
		
		self._columns.append (column)
		
		gtk_column = gtk.TreeViewColumn(column.label, gtk.CellRendererText(), text = len (self._columns) - 1)
		self.gtk_treeview.append_column (gtk_column)
		
	def gtk_on_row_activated (self, view, path, col):
		model = view.get_model ()
		iterator = model.get_iter (path)
		
		s = model.get_string_from_iter (iterator)
		if s in self.line_cache:
			self.selectedLine = self.line_cache[s]
			self.event_line_selected.call (self.line_cache[s])
		
		
disp.form.Table = TableGtk

class TableColumnGtk (ComponentGtk, disp.form.TableColumnBase):
	def __init__ (self, parent = None, column = None, label = None):
		
		self.col = column
		self.label = label
		ComponentGtk.__init__ (self, parent)
	
	def render (self, obj):
		if isinstance(obj, dict):
			return unicode (obj[self.col])
		else:
			return unicode (getattr(obj, self.col))

disp.form.TableColumn = TableColumnGtk

class ButtonGtk (ComponentGtk, disp.form.ButtonBase):
	def __init__(self, parent=None, text=""):

		self.gtk_object = gtk.Button (label = text)
		self.gtk_object.connect("clicked", self.gtk_on_clicked)
		
		ComponentGtk.__init__ (self, parent, False)
		self.event_clicked = disp.event.Event (self)
		
		self.gtk_object.show ()
		
	def gtk_on_clicked (self, button):
		self.event_clicked.call ()
	
	def setText (self, text):
		self.gtk_object.set_label (text)
	
	def getText (self):
		return self.gtk_object.get_label ()
	
	def getEventClicked (self):
		return self.event_clicked

disp.form.Button = ButtonGtk

class LineEditGtk (ComponentGtk, disp.form.LineEditBase):
	def __init__(self, parent=None, text="", size = None):
		
		self.gtk_object = gtk.Entry ()
		self.gtk_object.set_text (text)
		
		ComponentGtk.__init__ (self, parent, False)
		
	def getText (self):
		return self.gtk_object.get_text ()
	
	def setText (self, text):
		self.gtk_object.set_text (text)
		
disp.form.LineEdit = LineEditGtk

class StaticTextGtk (ComponentGtk, disp.form.StaticTextBase):
	def __init__(self, parent=None, text = ""):
		self.gtk_object = gtk.Label (text)
		ComponentGtk.__init__ (self, parent, False)
		
	def setText (self, text):
		self.gtk_object.set_text (text)
		
	def getText (self):
		return self.gtk_object.get_text ()
		
disp.form.StaticText = StaticTextGtk

class VBoxGtk (ContainerGtk, disp.form.VBoxBase):
	def __init__ (self, parent=None):
		self.gtk_object = gtk.VBox ()
		ContainerGtk.__init__ (self, parent, False)
		
	def append (self, component):
		self.gtk_object.pack_start (component.gtk_object, expand=component.gtk_expand, fill=component.gtk_fill, padding=component.gtk_padding)
		
	def gtk_set_child_packing (self, child, expand=True, fill=True, padding=4):
		self.gtk_object.set_child_packing (child.gtk_object, expand, fill, padding, gtk.PACK_START)
		
		if self.gtk_expand == False and expand:
			self.gtk_expand = True
			self._parent.gtk_set_child_packing (self)
		
disp.form.VBox = VBoxGtk

class VPaneGtk (ContainerGtk, disp.form.VPaneBase):
	def __init__ (self, parent=None):
		self.gtk_object = gtk.VPaned ()
		ContainerGtk.__init__ (self, parent, True)
		
		self.count = 0
		
	def append (self, component):
		if self.count == 0:
			self.gtk_object.add1 (component.gtk_object)
		else:
			self.gtk_object.add2 (component.gtk_object)
			
		self.count += 1
			
disp.form.VPane = VPaneGtk

class VButtonBoxGtk (ContainerGtk, disp.form.VButtonBoxBase):
	def __init__ (self, parent=None):
		self.gtk_object = gtk.VButtonBox ()
		ContainerGtk.__init__ (self, parent, False)
		
	def append (self, component):
		self.gtk_object.pack_start (component.gtk_object, expand=component.gtk_expand, fill=component.gtk_fill, padding=component.gtk_padding)
		
disp.form.VButtonBox = VButtonBoxGtk

class HBoxGtk (ContainerGtk, disp.form.HBoxBase):
	def __init__ (self, parent=None):
		
		self.gtk_object = gtk.HBox ()
		
		ContainerGtk.__init__ (self, parent, False)
		
	def append (self, component):
		self.gtk_object.pack_start (component.gtk_object, expand=component.gtk_expand, fill=component.gtk_fill, padding=component.gtk_padding)
		
	def gtk_set_child_packing (self, child, expand=True, fill=True, padding=4):
		self.gtk_object.set_child_packing (child.gtk_object, expand, fill, padding, gtk.PACK_START)
		
		if self.gtk_expand == False and expand:
			self.gtk_expand = True
			self._parent.gtk_set_child_packing (self)

disp.form.HBox = HBoxGtk

class HPaneGtk (ContainerGtk, disp.form.HPaneBase):
	def __init__ (self, parent=None):
		self.gtk_object = gtk.HPaned ()
		ContainerGtk.__init__ (self, parent, True)
		
		self.count = 0
		
	def append (self, component):
		if self.count == 0:
			self.gtk_object.add1 (component.gtk_object)
		else:
			self.gtk_object.add2 (component.gtk_object)
		self.count += 1
			
disp.form.HPane = HPaneGtk


class HButtonBoxGtk (ContainerGtk, disp.form.HButtonBoxBase):
	def __init__ (self, parent=None):
		self.gtk_object = gtk.HButtonBox ()
		ContainerGtk.__init__ (self, parent, False)
		
	def append (self, component):
		self.gtk_object.pack_start (component.gtk_object, expand=component.gtk_expand, fill=component.gtk_fill, padding=component.gtk_padding)
		
disp.form.HButtonBox = HButtonBoxGtk

class GridGtk (ContainerGtk, disp.form.GridBase):
	def __init__ (self, parent=None, rows=0, cols=0):
		
		self.rows_num = int(rows)
		self.cols_num = int(cols)
		
		self.gtk_object = gtk.Table (rows = self.rows_num, columns = self.cols_num)
		
		self.row = 0
		self.col = 0
		
		ContainerGtk.__init__ (self, parent, False)
		
	def append (self, component):
		#self.components.append (component)
		# self.gtk_object.pack_start (component.gtk_object, expand=component.gtk_expand, padding=component.gtk_padding)
		
		self.gtk_object.attach (component.gtk_object, self.col, self.col + 1, self.row, self.row + 1, gtk.FILL, gtk.FILL, 4, 4)
		
		self.col += 1
		if self.col >= self.cols_num:
			self.row += 1
			self.col = 0

disp.form.Grid = GridGtk

class TabBoxGtk (ContainerGtk, disp.form.TabBoxBase):
	def __init__ (self, parent=None):
		
		self.gtk_object = gtk.Notebook ()
		self.gtk_object.connect("switch-page", self.gtk_on_switch_page)
		
		ContainerGtk.__init__ (self, parent, True)
		
		self._pagemap = {}
		self._current_page = 0
		
	def addTab (self, component, label):
		self.gtk_label = gtk.Label (label)
		index = self.gtk_object.append_page (component.gtk_object, self.gtk_label)
		
		self._pagemap [index] = component
		
	def append (self, component):
		assert hasattr(component, "label")
		self.addTab (component, component.label)
		
	def gtk_hide (self):
		self._current_page = self.gtk_object.get_current_page()
		ContainerGtk.gtk_hide (self)
		
	def gtk_show (self):
		
		ContainerGtk.gtk_show (self)
		self.gtk_object.set_current_page (self._current_page)
		#self.gtk_object.show ()
		#self._pagemap[self._current_page]. ()
		
		#print "TabBoxGtk.gtk_show, current = " + str(self._current_page)
		
		#self.gtk_object.set_current_page (self._current_page)
		
	def gtk_on_switch_page (self, notebook, page, page_num):
		pass
		#self._current_page = page_num
		
		#print "TabBoxGtk.gtk_on_switch_page, current = " + str(self._current_page)

disp.form.TabBox = TabBoxGtk

class TabGtk (VBoxGtk, disp.form.TabBase):
	def __init__ (self, parent=None, label=""):
		self._label = label
		VBoxGtk.__init__ (self, parent)
		
	def setLabel (self, label):
		# TODO: upravit label v tabboxu
		self._label = label
		
	def getLabel (self):
		return self._label
	
disp.form.Tab = TabGtk

class CheckBoxGtk (ComponentGtk, disp.form.CheckBoxBase):
	def __init__(self, parent=None, text="", checked=False):
		
		self.gtk_object = gtk.CheckButton (text)
		ComponentGtk.__init__ (self, parent, False)
		
	def getText (self):
		return self.gtk_object.get_label ()
	
	def setText (self, text):
		self.gtk_object.set_label (text)
		
	def getChecked (self):
		return self.gtk_object.get_active()
	
	def setChecked (self, checked):
		self.gtk_object.set_active (checked)
		
disp.form.CheckBox = CheckBoxGtk


class SpacerGtk (ComponentGtk, disp.form.SpacerBase):
	def __init__(self, parent=None):
		self.gtk_object = gtk.Label ()
		ComponentGtk.__init__ (self, parent, True)

disp.form.Spacer = SpacerGtk

class RadioBoxGtk(ComponentGtk, disp.form.RadioBoxBase):
	def __init__(self, parent = None, option = None):
		self.gtk_object = gtk.VBox()
		ComponentGtk.__init__ (self, parent, False)
		
		self.gtk_options = []
	
	def setOption (self, option):
		for i in self.gtk_options:
			if unicode(i.get_label ()) == unicode(option):
				i.set_active (True)
	
	def getOption (self):
		for i in self.gtk_options:
			if i.get_active ():
				return i.get_label ()
	
	def addOption (self, option):
		if len(self.gtk_options) > 0:
			o = gtk.RadioButton (self.gtk_options[0], option)
		else:
			o = gtk.RadioButton (None, option)
			
		self.gtk_options.append (o)
		self.gtk_object.pack_start (o, expand=False)
	
	def removeOption (self, option):
		pass
	
disp.form.RadioBox = RadioBoxGtk

class FrameBoxGtk (ContainerGtk, disp.form.FrameBoxBase):
	def __init__ (self, parent=None, label = ""):
		self.gtk_object = gtk.Frame (label)
		ContainerGtk.__init__ (self, parent, False)
		
	def append (self, component):
		self.gtk_object.add (component.gtk_object)
		
	def setLabel (self, label):
		self.gtk_object.set_label (label)
		
	def getLabel (self):
		return self.gtk_object.get_label ()

	
disp.form.FrameBox = FrameBoxGtk
