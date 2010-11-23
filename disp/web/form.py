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
import disp.pobject

from mod_python import apache



def escape_xml (text):
	text = text.replace ("&", "&amp;")
	text = text.replace ("<", "&lt;")
	text = text.replace ("\"", "&quot;")
	text = text.replace ("'", "&apos;")
	return text

class ComponentWeb (disp.form.ComponentBase, disp.pobject.PObject):
	def __init__(self, parent=None):
		disp.pobject.PObject.__init__ (self, parent)
		self.visible = True
		
		# Setrime... 
		#if parent._root._init: self._dirty = False
		
	def web_in (self, path, val, context):
		pass
	
	def web_out (self, context):
		return ""
	
	def show (self):
		self.visible = True
		
	def hide (self):
		self.visible = False
		
	def append (self, component):
		pass
		
	#def _addChild (self, child, name = None):
		#disp.pobject.PObject._addChild (self, child, name)
		#self.append (child)

disp.form.Component = ComponentWeb

class ContainerWeb (disp.form.ContainerBase, ComponentWeb):
	def __init__ (self, parent=None):
		ComponentWeb.__init__ (self, parent)
		self.components = []
		
	def web_in (self, path, val, context):
		index = path[0]
		rest = path[1:]
		
		#apache.log_error ("ContainerWeb.web_in path = %s, val=%s" % (str(path), str(val)))
		
		comp = self._children [index]
		
		if hasattr(comp, "web_in"):
			comp.web_in (rest, val, context)
			
	def append(self, component):
		self.dirty ()
		self.components.append (component._name)
		
	def remove (self, component):
		self.dirty ()
		self.components.remove (component._name)
		
	def clear (self):
		self.dirty ()
		self.components = []
		
	def insertChild (self, child):
		disp.pobject.PObject.insertChild (self, child)
		
		#if isinstance(child, ComponentWeb):
		if hasattr(child, "web_out"):
			self.append (child)
		
disp.form.Container = ContainerWeb

class FormWeb (ContainerWeb, disp.form.FormBase):
	def __init__(self, parent=None):
		ContainerWeb.__init__ (self, parent)
			
		self.event_opened = disp.event.Event (self)
		self.event_closed = disp.event.Event (self)
		
	def web_out (self, context):
		#ret = "<html><body><form action=\"%s\" method=\"POST\">" % (context.url)
		
		if not self.visible:
			return ""
		
		ret = "<div class=\"form\">\n"

		for comp in self.components:
			comp = self._children[comp]
			#ret += "<div>"
			#if isinstance(comp, ComponentWeb):
			if hasattr(comp, "web_out"):
				ret += comp.web_out (context)
			#ret += "</div>"
		ret += "</div>\n"
		#ret = ret + "</form></body></html>"
		
		return ret
			
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
	

disp.form.Form = FormWeb

class TableWeb(ComponentWeb, disp.form.TableBase):
	def __init__(self, parent=None, rows=20):
		ComponentWeb.__init__ (self, parent)
		
		self.event_line_selected = disp.event.Event (self)
		self.page_size = int(rows)
		self.page = 0
		
		self._cursor = None
		self._columns = []
		
		self.selectedLine = None
		
		# Kurzor neni nad nasi kontrolou, musime se povazovat za dirty:
		#self._dirty = True
		#self.line_cache = {}
		
	def getEventLineSelected (self):
		return self.event_line_selected

	def setCursor (self, cursor):
		self._cursor = cursor

	def getCursor (self):
		return self._cursor
	
	def append (self, column):
		self._columns.append (column._name)
		
	def update (self):
		self.selectedLine = None
	
	def insertChild (self, child):
		disp.pobject.PObject.insertChild (self, child)
		
		#if isinstance(child, TableColumnWeb):
		if hasattr(child, "render"):
			self.append (child)
			
	def getSelectedLine (self):
		
		cursor = self.cursor
		
		if cursor != None and self.selectedLine != None:
			cursor.begin ()
			line = cursor[self.selectedLine]
			cursor.end ()
			
			return line
		
		return None
		
	def web_in (self, path, val, context):
		index = path[0]
		rest = path[1:]
		
		if index == "page":
			self.dirty ()
			self.page = int (val.value)
			
			if self.page < 0:
				self.page = 0
				
		elif index == "select":
			#line = int (val)
			#if line in self.line_cache:
			
			self.dirty ()
			
			cursor = self.cursor
			
			cursor.begin ()
			
			self.selectedLine = int(val.value)
			
			try:
				line = cursor[self.selectedLine]
			except:
				line = None
			
			if line:
				context.addEvent (self.event_line_selected, line)
				
			cursor.end ()
	
	def web_out (self, context):
		#ret = "<h1>%d</h1>" % (self.page)
		ret = ""
		
		if not self.visible:
			return ""
		

		cursor = self.cursor
		if cursor != None:
			
			ret += "<div class=\"table\">"
			ret += "<table class=\"table\"><tbody>"
			ret += "<tr class=\"table_header\">"
		
			#if not self.event_line_selected.isEmpty ():
				#ret += "<td></td>"
					
			for column in self._columns:
				column = self._children[column]
				ret += "<td>%s</td>" % escape_xml (column.label)
			ret += "</tr>"
			
			cursor.begin ()
			
			count_total = cursor.count ()
			
			index_begin = self.page * self.page_size
			index_end = (self.page + 1) * self.page_size
			
			if index_begin < 0:
				self.page = 0
				index_begin = 0
			if index_end > count_total:
				self.page = count_total / self.page_size
				index_end = count_total

			index = index_begin
			for line in cursor[index_begin:index_end]:
				
				if self.selectedLine == index:
					ret += "<tr class=\"table_selected\">"
				else:
					ret += "<tr>"
					
				
				#if not self.event_line_selected.isEmpty ():
				#ret += "<td><a href=\"%s?%s\">select</a></td>" % ((context.url, self._id+".select="+str(index)))
					
				for column in self._columns:
					column = self._children [column]
					render = escape_xml (column.render(line))
					
					if render == "":
						render = "&nbsp;"
						
					ret += "<td><a href=\"%s?%s\">" % ((context.url, self._id+".select="+str(index))) + render + "</a></td>"
				ret += "</tr>"
					
				index = index + 1

			cursor.end ()
			
			ret += "</tbody></table>"
		
			ret += "<div class=\"table_nav\">Page "
			
			for i in range(10):
				page = self.page - 5 + i
				if page >= 0 and page <= count_total / self.page_size:
					ret += "<a href=\"%s?%s\">%d</a> " % (context.url, self._id+".page="+str(page), page + 1)
			#ret += "<a href=\"%s?%s\">Next</a>" % (context.url, self._id+".page="+str(self.page+1))
			ret += "</div>"
			
			ret += "</div>"
		
		return ret
		
disp.form.Table = TableWeb

class TableColumnWeb (ComponentWeb, disp.form.TableColumnBase):
	
	def __init__ (self, parent = None, column = None, label = None):
		ComponentWeb.__init__ (self, parent)
		self.notdirty()
		
		self.col = column
		self.label = label
	
	def render (self, obj):
		if isinstance(obj, dict):
			return unicode (obj[self.col])
		else:
			return unicode (getattr(obj, self.col))

disp.form.TableColumn = TableColumnWeb

class ButtonWeb (ComponentWeb, disp.form.ButtonBase):
	def __init__(self, parent=None, text=""):
		ComponentWeb.__init__ (self, parent)
		self.notdirty()
		
		self._text = text
		self.event_clicked = disp.event.Event (self)
		
		#apache.log_error ("ButtonWeb.ctor (%s) id = %s" % (str(self), str(self._id)))
		
				
	def getEventClicked (self):
		return self.event_clicked

	def setText (self, text):
		self.dirty ()
		self._text = text

	def getText (self):
		return self._text
		
	def web_in (self, path, val, context):
		context.addEvent (self.event_clicked)
		
	def web_out (self, context):
		
		if not self.visible:
			return ""
		
		return "<input class=\"button\" type=\"submit\" id=\"%s\" name=\"%s\" value=\"%s\" />" % (self._id, self._id, escape_xml (self._text))

disp.form.Button = ButtonWeb


class LineEditWeb (ComponentWeb, disp.form.LineEditBase):
	def __init__(self, parent=None, text="", size = None):
		ComponentWeb.__init__ (self, parent)
		self.notdirty()
		self._text = text
		
		if size:
			self._size = int(size)
		else:
			self._size = 20
		
	def setText (self, text):
		self.dirty ()
		self._text = text

	def getText (self):
		return self._text
		
	def web_in (self, path, val, context):
		self.dirty ()
		self._text = val.value.decode("utf8")
		
	def web_out (self, context):
		
		if not self.visible:
			return ""
		
		return "<input class=\"line_edit\" type=\"text\" id=\"%s\" name=\"%s\" value=\"%s\" size=\"%s\"/>" % (self._id, self._id, escape_xml (self._text), self._size)
		
disp.form.LineEdit = LineEditWeb

class StaticTextWeb (ComponentWeb, disp.form.StaticTextBase):
	def __init__(self, parent=None, text = ""):
		ComponentWeb.__init__ (self, parent)
		self.notdirty()
		self._text = text
		
	def setText (self, text):
		self.dirty ()
		self._text = unicode(text)

	def getText (self):
		return self._text

	def web_out (self, context):
		if self.visible:
			return "<div class=\"static_text\">"+escape_xml (self._text)+"</div>"
		else:
			return ""
		
disp.form.StaticText = StaticTextWeb

class VBoxWeb (ContainerWeb, disp.form.VBoxBase):
	def __init__ (self, parent=None):
		ContainerWeb.__init__ (self, parent)
		self.notdirty()
		
		
	def web_out (self, context):
		
		if not self.visible:
			return ""
		
		ret = ""
		ret += "<div>"
		
		for comp in self.components:
			comp = self._children[comp]
			#if isinstance (comp, ComponentWeb):
			if hasattr(comp, "web_out"):
				ret += "<div style=\"display:block\">"
				ret += comp.web_out (context)
				ret += "</div>"

		ret += "</div>"
		return ret
		
disp.form.VBox = VBoxWeb
disp.form.VButtonBox = VBoxWeb


class HBoxWeb (ContainerWeb, disp.form.HBoxBase):
	def __init__ (self, parent=None):
		ContainerWeb.__init__ (self, parent)
		self.notdirty()
		
	def web_out (self, context):
		
		if not self.visible:
			return ""
		
		ret = ""
		ret += "<div>"
		
		for comp in self.components:
			comp = self._children[comp]
			#if isinstance (comp, ComponentWeb):
			if hasattr(comp, "web_out"):
				ret += "<div style=\"display:inline\">"
				ret += comp.web_out (context)
				ret += "</div>"

		ret += "</div>"
		return ret
		
disp.form.HBox = HBoxWeb
disp.form.HButtonBox = HBoxWeb


class HPaneWeb (ContainerWeb, disp.form.HPaneBase):
	def __init__ (self, parent=None):
		ContainerWeb.__init__ (self, parent)
		self.notdirty()
		
	def web_out (self, context):
		
		if not self.visible:
			return ""
		
		ret = ""
		ret += "<table class=\"hpane\"><tbody><tr valign=\"top\">"
		
		for comp in self.components:
			comp = self._children[comp]
			#if isinstance (comp, ComponentWeb):
			if hasattr(comp, "web_out"):
				ret += "<td class=\"hpane_td\">"
				ret += comp.web_out (context)
				ret += "</td>"

		ret += "</tr></tbody></table>"
		return ret
		
disp.form.HPane = HPaneWeb

class VPaneWeb (ContainerWeb, disp.form.VPaneBase):
	def __init__ (self, parent=None):
		ContainerWeb.__init__ (self, parent)
		self.notdirty()
		
	def web_out (self, context):
		
		if not self.visible:
			return ""
		
		ret = ""
		ret += "<table class=\"vpane\">"
		
		for comp in self.components:
			comp = self._children[comp]
			#if isinstance (comp, ComponentWeb):
			if hasattr(comp, "web_out"):
				ret += "<tr><td>"
				ret += comp.web_out (context)
				ret += "</td></tr>"

		ret += "</table>"
		return ret
		
disp.form.VPane = VPaneWeb

class GridWeb (ContainerWeb, disp.form.GridBase):
	def __init__ (self, parent=None, rows=0, cols=0):
		ContainerWeb.__init__ (self, parent)
		self.notdirty()
		
		self.rows_num = int(rows)
		self.cols_num = int(cols)
		
	def web_out (self, context):
		
		if not self.visible:
			return ""
		
		ret = ""
		ret += "<table class=\"grid\"><tbody>"
		
		i = 0
		for comp in self.components:
			comp = self._children[comp]
			if hasattr(comp, "web_out"):
			#if isinstance (comp, ComponentWeb):
			
				if (i % self.cols_num) == 0:
					ret += "<tr>"
				
				ret += "<td>"
				ret += comp.web_out (context)
				ret += "</td>"
			
				if (i % self.cols_num) == (self.cols_num - 1):
					ret += "</tr>"
					
				i += 1

		ret += "</tbody></table>"
		return ret
		
disp.form.Grid = GridWeb


class TabBoxWeb (ContainerWeb, disp.form.TabBoxBase):
	def __init__ (self, parent=None):
		ContainerWeb.__init__ (self, parent)
		self.notdirty()
		
		self._index = 0
		self._tabs = []
		
	def addTab (self, component, label):
		assert component._parent == self
		assert hasattr(component, "label")
		self._tabs.append (component._name)
		self.dirty ()
		
	def web_in (self, path, val, context):
		index = path[0]
		rest = path[1:]
		
		if index == "__select":
			self._index = int(val.value)
			self.dirty ()
		else:
			comp = self._children [index]
			if hasattr(comp, "web_in"):
				comp.web_in (rest, val, context)
		
	def web_out (self, context):
		
		if not self.visible:
			return ""
		
		if self._index < 0 or self._index >= len(self._tabs):
			self._index = 0
		
		ret = ""
		
		ret += "<div class=\"tabbox\">"
		ret += "<div class=\"tabbox_tabs\">"
		
		# Render tabs with labels
		for i in range (len (self._tabs)):
			component = self._tabs [i]
			component = self._children[component]
			
			if i == self._index:
				ret += " <span class=\"tabbox_selected\">"
			else:
				ret += " <span>"
			ret += "<a href=\"%s?%s\">%s</a></span> " % ((context.url, self._id+".__select="+str(i), escape_xml (component.label)))
		ret += "</div>"
		
		# Display the selected tab:
		if len(self._tabs) > 0:
			
			ret += "<div class=\"tabbox_panel\">"
			
			tab = self._tabs [self._index]
			tab = self._children[tab]
			ret += tab.web_out (context)
			
			ret += "</div>"

		ret += "</div>"
		return ret
		
disp.form.TabBox = TabBoxWeb


class TabWeb (VBoxWeb, disp.form.TabBase):
	def __init__ (self, parent=None, label=""):
		VBoxWeb.__init__ (self, parent)
		
		self._label = label
		self._parent.addTab (self, self._label)
		
	def getLabel (self):
		return self._label
	
	def setLabel (self, label):
		self._label = label
		
disp.form.Tab = TabWeb

class CheckBoxWeb (ComponentWeb, disp.form.CheckBoxBase):
	def __init__(self, parent=None, text="", checked=False):
		ComponentWeb.__init__ (self, parent)
		self.notdirty()
		
		self._root.web_event_post.addHandler (self.web_on_post)
		
		self._text = text
		self._checked = checked
		
	def setText (self, text):
		self._text = text
		self.dirty ()

	def getText (self):
		return self._text
	
	def setChecked (self, checked):
		self._checked = checked
		self.dirty ()
		
	def getChecked (self):
		return self._checked
		
	def web_on_post (self):
		# if not checked, web_in is never called, so we reset state before input...
		self._checked = False
		self.dirty ()
		
	def web_in (self, path, val, context):
		# this is called only if checked...
		self._checked = True
		self.dirty ()
		
	def web_out (self, context):
		
		if not self.visible:
			return ""
		
		c = ""
		if self._checked:
			c = "checked=\"checked\""
		return "<input class=\"checkbox\" type=\"checkbox\" id=\"%s\" name=\"%s\" value=\"check\" %s/> %s" % (self._id, self._id, c, escape_xml(self._text))
		
disp.form.CheckBox = CheckBoxWeb

class SpacerWeb (ComponentWeb, disp.form.SpacerBase):
	def __init__(self, parent=None):
		ComponentWeb.__init__ (self, parent)
		
disp.form.Spacer = SpacerWeb


class FileUploadWeb (ComponentWeb):
	def __init__(self, parent=None, file=None):
		ComponentWeb.__init__ (self, parent)
		self.notdirty()
		
		self.file = None
		
	def setFile (self, file):
		self.file = file
		self.dirty ()
		
	def web_in (self, path, val, context):
		
		name = path[0]
		
		#apache.log_error ("FileUploadWeb.web_in path = %s, val=%s" % (str(path), str(val)))
		
		if name == "__file":
			self.file.readFrom (val.file)
			# little hack:
			self._root.readFile (None)
		elif name == "__cancel":
			self._root.readFile (None)
		
	def web_out (self, context):
		return "<div><input type=\"file\" id=\"%s\" name=\"%s\" /> <input type=\"submit\"/> <a href=\"%s?%s\">%s</a> </div>" % (self._id+".__file", self._id+".__file", context.url, self._id+".__cancel=1", "Cancel")

class RadioBoxWeb(ComponentWeb, disp.form.RadioBoxBase):
	def __init__(self, parent = None, option = None):
		ComponentWeb.__init__ (self, parent)
		self.notdirty()
		
		self._options = []
		self._option = option
	
	def setOption (self, option):
		self._option = option
		self.dirty ()
	
	def getOption (self):
		return self._option
	
	def addOption (self, option):
		self._options.append (option)
		self.dirty ()
	
	def removeOption (self, option):
		self._options.remove (option)
		
	def web_in (self, path, val, context):
		self._option = val.value
		self.dirty ()

	def web_out (self, context):
		ret = "<div>"
		for option in self._options:
			escaped = escape_xml (option)
			if unicode(option) == unicode(self._option):
				ret += "<input type=\"radio\" name=\"%s\" checked=\"checked\" id=\"%s\" value=\"%s\"/>%s<br/>" % (self._id, self._id, escaped, escaped)
			else:
				ret += "<input type=\"radio\" name=\"%s\" id=\"%s\" value=\"%s\"/>%s<br/>" % (self._id, self._id, escaped, escaped)
		
		ret += "</div>"
		
		return ret
				
disp.form.RadioBox = RadioBoxWeb

class FrameBoxWeb(ContainerWeb, disp.form.FrameBoxBase):
	def __init__ (self, parent = None, label = ""):
		ContainerWeb.__init__ (self, parent)
		self.notdirty()
		
		self._label = label
		
	def setLabel (self, label):
		self._label = label
		self.dirty ()
		
	def getLabel (self):
		return self._label
	
	def web_out (self, context):
		
		if not self.visible:
			return ""
		
		ret = "<fieldset>"
		ret += "<legend>"
		ret += escape_xml (self._label)
		ret += "</legend>"
		
		ret += "<div>"
		
		for comp in self.components:
			comp = self._children[comp]
			if hasattr(comp, "web_out"):
				ret += "<div style=\"display:block\">"
				ret += comp.web_out (context)
				ret += "</div>"

		ret += "</div>"
		
		ret += "</fieldset>"
		return ret
			
disp.form.FrameBox = FrameBoxWeb
