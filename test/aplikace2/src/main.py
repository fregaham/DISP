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
from disp.cursor import *
from disp.xmlui import *

class MojeData (Cursor):
  def __init__ (self):
    Cursor.__init__ (self)
    self.data = []

  def __iter__ (self):
    return self.data.__iter__ ()

  def __getitem__ (self, i):
    return self.data[i]

  def __len__ (self):
    return len(self.data)

  def add(self, a, b, c):
    self.data.append ({"a":a,"b":b,"c":c})

class Main (Application):
  def initialize (self):
    self.title = "Hello, world"
    form = Form (self)

    uiloader = XMLUIBuilder ()
    uiloader.loadFile ('form.xml', self, form)

    self.data = MojeData ()

    for i in range(100):
      self.data.add (i, i*i, i*i*i)

    self.table.cursor = self.data

    self.radio.addOption ("Black")
    self.radio.addOption ("Green")
    self.radio.addOption ("Yellow")

    form.open ()

  def onClick (self):
    self.static.text = self.edit.text + ", " + str(self.check.checked) + ", " + self.radio.option

  def onSelected (self, line):
    self.static.text = "A = %s, B = %s, C = %s" % (line["a"], line["b"], line["c"])

