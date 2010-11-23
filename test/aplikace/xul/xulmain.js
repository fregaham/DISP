/* copyright (C) 2006 Marek Schmidt

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA. */


var g_components = {};
var g_ctors = {};

var g_call_queue = [];

var xulns = "http://www.mozilla.org/keymaster/gatekeeper/there.is.only.xul";
var htmlns = "http://www.w3.org/1999/xhtml";


function getComponent (id) {
	return g_components [id];
}

// Component
function Component (id) {

	if (id != null) {
		this.id = id;
		g_components [id] = this;
		
		this.call_queue = [];
		this.has_joined_document = false;
	}	
}

Component.prototype.show = function (args) {
	var e = this.getElement ();
	e.hidden = false;
}

Component.prototype.hide = function (args) {
	var e = this.getElement ();
	e.hidden = true;
}

/** Element byl přidán do dokumentového stromu */
Component.prototype.onJoinedDocument = function () {

	this.has_joined_document = true;

	for (var i in this.call_queue) {
		var call = this.call_queue [i];
		
		this [call[0]] (call [1]);
	}
	
	this.call_queue = [];
}

Component.prototype.getElement = function () {
	return document.getElementById (this.id);
}

Component.prototype.serverCall = function (method_name, args) {
	g_call_queue.push (["call", this.id, method_name, args]);
}

/** Vrací stav objektu. Posílá se na server. Může vrátit null pokud nechce nic poslat. */
Component.prototype.getState = function () {
	return null;
}

// Container
function Container (id) {
	Component.apply (this, [id]);
	
	if (id != null) {
		this.components = [];
	}
}
Container.prototype = new Component ();
Container.prototype.constructor = Container;

/** Element byl přidán do dokumentového stromu */
Container.prototype.onJoinedDocument = function () {
	Component.prototype.onJoinedDocument.apply (this, []);
	
	for (var i in this.components) {
		var component = this.components [i];
		component.onJoinedDocument ();
	}
}

Container.prototype.add = function (id) {
	var obj = g_components [id];

	var e = this.element;
	e.appendChild (obj.element);
	
	this.components.push (obj);
	
	if (this.has_joined_document) {
		obj.onJoinedDocument ();
	}
}

Container.prototype.remove = function (id) {

	var obj = g_components [id];

	var e = this.element;
	e.removeChild (obj.element);
	
	for (var i in this.components) {
		var component = this.components[i];
		if (component == obj) {
		
			this.components.splice(i, 1);
			break;
		}
	}
}

// Application
function Application (id) {
	Container.apply (this, [id]);
	this.element = document.getElementById (id);
	
	this.has_joined_document = true;
}

Application.prototype = new Container ();
Application.prototype.constructor = Application;

/*Application.prototype.add = function (id) {
	Container.prototype.add.apply (this, [id]);
	
	var comp = getComponent (id);
	comp.onJoinedDocument ();
}*/

Application.prototype.display = function (id) {

	var deck = this.getElement ();
	
	var i = 0;
	for (i in this.components) {
		if(this.components[i].id == id) {
			deck.selectedIndex = i;
			return;
		}
	}
}

Application.prototype.set_title = function (txt) {
	// var wnd = document.getElementById("__window__");
	// wnd.setAttribute ("title", txt.toString());
	//wnd.title = txt.toString ();
	document.title = txt.toString ();
}

// Form
function Form (id) {
	Container.apply (this, [id]);
	this.element = document.createElement ("vbox");
	this.element.id = id;
	
	this.element.setAttribute ("flex", 1);
	
	//this.element.setAttribute("style", "overflow: auto;");
}

Form.prototype = new Container ();
Form.prototype.constructor = Form;
g_ctors["Form"] = Form;

// VBox
function VBox (id) {
	Container.apply (this, [id]);
	
	this.element = document.createElement ("vbox");
	this.element.setAttribute ("flex", 1);
	/*this.element.setAttribute ("align", "start");
	this.element.setAttribute ("pack", "start");*/
	this.element.id = id;
}

VBox.prototype = new Container ();
VBox.prototype.constructor = VBox;
g_ctors["VBox"] = VBox;

// HBox
function HBox (id) {
	Container.apply (this, [id]);
	
	this.element = document.createElement ("hbox");
	
	this.element.setAttribute ("flex", 1);
	/*this.element.setAttribute ("align", "start");
	this.element.setAttribute ("pack", "start");*/
	this.element.id = id;
}

HBox.prototype = new Container ();
HBox.prototype.constructor = HBox;
g_ctors["HBox"] = HBox;
			
// VButtonBox
function VButtonBox (id) {
	Container.apply (this, [id]);
	
	this.element = document.createElement ("vbox");
	this.element.setAttribute ("flex", 0);
	this.element.setAttribute ("align", "start");
	this.element.setAttribute ("pack", "start");
	this.element.id = id;
}

VButtonBox.prototype = new Container ();
VButtonBox.prototype.constructor = VButtonBox;
g_ctors["VButtonBox"] = VButtonBox;

// HButtonBox
function HButtonBox (id) {
	Container.apply (this, [id]);
	
	this.element = document.createElement ("hbox");
	this.element.setAttribute ("flex", 0);
	this.element.setAttribute ("align", "start");
	this.element.setAttribute ("pack", "start");
	this.element.id = id;
}

HButtonBox.prototype = new Container ();
HButtonBox.prototype.constructor = HButtonBox;
g_ctors["HButtonBox"] = HButtonBox;
			
			
// VPane
function VPane (id) {
	Container.apply (this, [id]);
	
	this.element = document.createElement ("vbox");
	this.element.setAttribute ("flex", 1);
	this.element.id = id;
}

VPane.prototype = new Container ();
VPane.prototype.constructor = VPane;
g_ctors["VPane"] = VPane;

VPane.prototype.add = function (id) {
	
	if (this.components.length >= 1) {
		var splitter = document.createElement ("splitter");
		this.element.appendChild (splitter);
	}
	
	Container.prototype.add.apply (this, [id]);
}

// HPane
function HPane (id) {
	Container.apply (this, [id]);
	
	this.element = document.createElement ("hbox");
	this.element.setAttribute ("flex", 1);
	this.element.id = id;
}

HPane.prototype = new Container ();
HPane.prototype.constructor = HPane;
g_ctors["HPane"] = HPane;

HPane.prototype.add = function (id) {
	
	if (this.components.length >= 1) {
		var splitter = document.createElement ("splitter");
		this.element.appendChild (splitter);
	}
	
	Container.prototype.add.apply (this, [id]);
}

// StaticText
function StaticText (id) {
	Component.apply (this, [id]);
	
	this.element = document.createElementNS (xulns,  "label");
	this.element.id = id;
	
}

StaticText.prototype = new Component ();
StaticText.prototype.constructor = StaticText;
g_ctors["StaticText"] = StaticText;

StaticText.prototype.set_text = function (txt) {
	var e = this.getElement ();
	//e.setAttribute ("value", txt);
	e.value = txt;
}

function alertobject (obj) {
	s = ""
	for (var property in obj) {
		s += property + " ";
	}
	
	alert (s);
}

// LineEdit
function LineEdit (id) {
	Component.apply (this, [id]);
	
	this.element = document.createElementNS (xulns,  "textbox");
	this.element.id = id;
	
	//this.element.setAttribute("flex", 1);
	// alert (this.element.className);
	//alertobject (this.element);
}

LineEdit.prototype = new Component ();
LineEdit.prototype.constructor = LineEdit;
g_ctors["LineEdit"] = LineEdit;

LineEdit.prototype.set_text = function (txt) {
	var e = this.getElement ();
	e.value = txt;
}

LineEdit.prototype.set_size = function (size) {
	var e = this.getElement ();
	e.size = size;
}

LineEdit.prototype.getState = function () {
	return this.getElement ().value;
}

// Button
function Button (id) {
	Component.apply (this, [id]);
	this.element = document.createElement ("button");
	this.element.id = id;
	//this.element.width = "100";
	
	
}

Button.prototype = new Component ();
Button.prototype.constructor = Button;
g_ctors["Button"] = Button;

Button.prototype.set_text = function (txt) {
	var e = this.getElement ();
	e.setAttribute ("label", txt);
}

Button.prototype.on_command = function () {
	//alert ("click!");
	this.serverCall ("on_command", null);
	sendState ();
}

Button.prototype.onJoinedDocument = function () {
	Component.prototype.onJoinedDocument.apply (this, []);
	
	var e = this.getElement ();
	
	var handler = new Object();
	handler.button = this;
	handler.handleEvent = function (event) {
		this.button.on_command ();
	}
		
	this.element.addEventListener ("command", handler, false);
}

// table
function Table (id) {

	//alert("table: " + id);

	Component.apply (this, [id]);
	this.element = document.createElement ("tree");
	var element_treecols = document.createElement ("treecols");
	var element_treechildren = document.createElement ("treechildren");
	
	
	
	this.element.id = id;
	element_treecols.id = id + "._treecols";
	element_treechildren.id = id + "._treechildren";
	
	this.element.appendChild (element_treecols);
	this.element.appendChild (element_treechildren);
	
	this.element.setAttribute("flex", 1);
	//this.element.setAttribute("rows", 30);
	this.element.setAttribute("hidecolumnpicker", true);
	
	//this.element_treechildren = element_treechildren;
	//this.element_treecols = element_treecols;
}

Table.prototype = new Component ();
Table.prototype.constructor = Table;
g_ctors["Table"] = Table;

Table.prototype.getTreeCols = function () {
	return document.getElementById (this.id + "._treecols");
}

Table.prototype.getTreeChildren = function () {
	return document.getElementById (this.id + "._treechildren");
}
		
Table.prototype.add_column = function (title) {
	var treecol = document.createElement ("treecol");
	
	treecol.setAttribute("label", title);
	treecol.setAttribute("flex", 1);
	
	this.getTreeCols ().appendChild (treecol);
}

Table.prototype.set_rows = function (rows) {
	this.element.setAttribute("rows", rows);
}

Table.prototype.update = function (data) {

	// alert ("update, id = " + this.id.toString()+ ", data="+data.toString())
	
	// var newchildren = this.getTreeChildren();
	//alert ("update: this.id=" + this.id + ", children.id = " + newchildren.id + ",data = " + data.toString());
	
	//clearElement (newchildren);
	var newchildren = document.createElement ("treechildren");
	newchildren.id = this.id + "._treechildren";
	
	for (var i in data) {
		var line = data[i];
		
		var item = document.createElement ("treeitem");
		var row = document.createElement ("treerow");
		
		for (var j in line) {
			var label = line[j];
			
			var cell = document.createElement ("treecell");
			cell.setAttribute ("label", label);
			
			//alert ("label = " + label);
			
			row.appendChild (cell);
		}
		
		item.appendChild (row);
		newchildren.appendChild (item);
	}
	
	var element =  document.getElementById (this.id)
	var oldchildren = this.getTreeChildren();
	
	/*alert ("element");
	alertobject(element);
	
	alert ("old");
	alertobject (oldchildren);
	
	alert("new");
	alertobject (newchildren);*/
	
	element.removeChild (oldchildren);
	element.appendChild (newchildren);
	
	
	//this.element_treechildren = newchildren;
}

Table.prototype.on_select = function () {
	this.serverCall ("on_select", this.getElement ().currentIndex);
	sendState ();
}

Table.prototype.onJoinedDocument = function () {

	Component.prototype.onJoinedDocument.apply (this, []);

	var handler = new Object();
	handler.table = this;
	handler.handleEvent = function (event) {
		this.table.on_select ();
	}
	
	this.element.addEventListener ("select", handler, false);
}

// Grid
function Grid (id) {
	Container.apply (this, [id]);
	
	this.element = document.createElement ("grid");
	this.element.id = id;
	
	this.element_cols = document.createElement ("columns");
	//this.element_cols.id = id + "/_cols";
	this.element_rows = document.createElement ("rows");
	//this.element_rows.id = id + "/_rows";
	
	this.element.appendChild (this.element_cols);
	this.element.appendChild (this.element_rows);
	
	this.rows_num = 0;
	this.cols_num = 0;
	
	this.current_row = null;
	this.current_col = 0;
}

Grid.prototype = new Container ();
Grid.prototype.constructor = Grid;
g_ctors["Grid"] = Grid;

/*Grid.prototype.getColumns = function () {
	return document.getElementById (this.id + "/_columns");
}

Grid.prototype.getRows = function () {
	return document.getElementById (this.id + "/_rows");
}*/


/** 
	Set number of columns and rows. 
		size == [rows, cols] 
*/
Grid.prototype.set_size = function (size) {
	this.rows_num = size [0];
	this.cols_num = size [1];
	
	// TODO: recreate columns and rows...
	var new_rows = document.createElement ("rows");
	var new_cols = document.createElement ("columns");
	
	// This is row-oriented, so prepare columns...
	for (var i = 0; i < this.cols_num; ++i) {
		var col = document.createElement ("column");
		//col.setAttribute ("flex", 1);
		new_cols.appendChild (col);
	}
	
	// And create rows with components
	j = 0;
	var row = null;
	for (var i in this.components) {
		var component = this.components [i];
		
		if (row == null || j >= this.cols_nums) {
			row = document.createElement ("row");
			new_rows.appendChild (row);
			
			j = 0;
		}
		
		row.appendChild (component.element);
		
		j = j + 1;
	}
	
	clearElement (this.element);
	this.element.appendChild (new_cols);
	this.element.appendChild (new_rows);
	
	this.element_cols = new_cols;
	this.element_rows = new_rows;
}

Grid.prototype.add = function (id) {
	var obj = g_components [id];
	
	// Row filled... adding row.
	// Note... if cols_num is zero, we will create row for each entry.
	if (this.current_row == null || this.current_col >= this.cols_num) {
		this.current_row = document.createElement ("row");
		this.element_rows.appendChild (this.current_row);
		
		this.current_col = 0;
	}
	
	//alert ("Grid.prototype.add");
	//alertobject (obj);
		
	this.current_row.appendChild (obj.element);
	this.components.push (obj);
	
	if (this.has_joined_document) {
		obj.onJoinedDocument ();
	}
	
	this.current_col = this.current_col + 1;
}


// TabBox
function TabBox (id) {
	Container.apply (this, [id]);
	
	this.element = document.createElement ("tabbox");
	this.element.id = id;
	
	this.element_tabs = document.createElement ("tabs");
	this.element_tabs.id = id + "/_tabs";
	this.element_tabpanels = document.createElement ("tabpanels");
	this.element_tabpanels.id = id + "/_tabpanels";
	
	this.element.appendChild (this.element_tabs);
	this.element.appendChild (this.element_tabpanels);
	
	this.has_tabs = false;
	// this.tabs = [];
}

TabBox.prototype = new Container ();
TabBox.prototype.constructor = TabBox;
g_ctors["TabBox"] = TabBox;

TabBox.prototype.add = function (id) {

	var obj = g_components [id];
	
	this.components.push (obj);
	
	if (this.has_joined_document) {
	
		var element_tabs = document.getElementById(this.id + "/_tabs");
		var element_tabpanels = document.getElementById(this.id + "/_tabpanels");
		
		var tab = document.createElement ("tab");
		tab.id = obj.id + "/tab";
		tab.setAttribute ("label", obj.id);
		
		if (!this.has_tabs) {
			tab.setAttribute ("selected", "true");
			this.has_tabs = true;
		}
		else {
			tab.setAttribute ("selected", "false");
		}
		
		element_tabs.appendChild (tab);
		
		var tabpanel = document.createElement ("tabpanel");
		element_tabpanels.appendChild (tabpanel);
		
		tabpanel.appendChild (obj.element);
	
		obj.onJoinedDocument ();
	}
	else {
		alert ("adding tab before joining document!");
	}
}

TabBox.prototype.set_tab_label = function (args) {
	var id = args[0];
	var label = args[1];
	
	var tab = document.getElementById (id + "/tab");
	tab.setAttribute ("label", label);
}

// Tab
function Tab (id) {
	Container.apply (this, [id]);
	this.element = document.createElement ("vbox");
	this.element.id = id;
	this.element.setAttribute ("flex", 1);
}

Tab.prototype = new Container ();
Tab.prototype.constructor = Tab;
g_ctors["Tab"] = Tab;


/** CheckBox */
function CheckBox (id) {
	Component.apply (this, [id]);
	
	this.element = document.createElementNS (xulns,  "checkbox");
	this.element.id = id;
}

CheckBox.prototype = new Component ();
CheckBox.prototype.constructor = CheckBox;
g_ctors["CheckBox"] = CheckBox;

CheckBox.prototype.set_text = function (txt) {
	var e = this.getElement ();
	e.label = txt;
}

CheckBox.prototype.set_checked = function (ch) {
	var e = this.getElement ();
	e.checked = ch;
}

CheckBox.prototype.getState = function () {
	//alert ("getState !!!");
	// alertobject(this.getElement ());
	//alert(this.id);
	return this.getElement ().checked;
}


/** Spacer */
function Spacer (id) {
	Component.apply (this, [id]);
	
	this.element = document.createElementNS (xulns,  "spacer");
	this.element.id = id;
	this.element.setAttribute("flex", 1)
}

Spacer.prototype = new Component ();
Spacer.prototype.constructor = Spacer;
g_ctors["Spacer"] = Spacer;

/** RadioBox */
function RadioBox (id) {
	Component.apply (this, [id]);

	this.element = document.createElementNS (xulns, "radiogroup");
	this.element.id = id;
}

RadioBox.prototype = new Component ();
RadioBox.prototype.constructor = RadioBox;
g_ctors["RadioBox"] = RadioBox;

RadioBox.prototype.set_option = function (option) {
	var e = this.getElement ();

	var list = e.getElementsByAttribute ("label", option);
	if (list.length > 0) {
		var radio = list[0];
		e.selectedItem = radio;
	}
}

RadioBox.prototype.add_option = function (option) {
	var e = this.getElement ();
	e.appendItem (option);
}

RadioBox.prototype.getState = function () {
	var e = this.getElement ();
	var radio = e.selectedItem;

	if(radio != null) {
		return radio.label;
	}
	else {
		return null;
	}
}

// FrameBox
function FrameBox (id) {
	Container.apply (this, [id]);
	
	this.element = document.createElementNS (xulns, "groupbox");
	this.element.id = id;

	this.element_caption = document.createElementNS(xulns, "caption");
	this.element_caption.id = id + "/caption";
	this.element.appendChild (this.element_caption);
}

FrameBox.prototype = new Container ();
FrameBox.prototype.constructor = FrameBox;
g_ctors["FrameBox"] = FrameBox;

FrameBox.prototype.set_label  = function (label) {
	var e = document.getElementById (this.id + "/caption");
	e.label = label;
}

// others...
function start () {

	uploadBuild ();

	var app = new Application("__root__");
	//sendMessage ("init");
	
	var req = new XMLHttpRequest();
	req.open('GET', './handler.py?init=1', false);
	req.send(null);
	
	msg_in = JSON.parse (req.responseText);
	parseCommands (msg_in);
	
	//alert (req.responseText);
}

function login () {
}

/** Pošle zprávu na server a zpracuje odpověď */
function sendMessage (msg) {

	var string = JSON.stringify(msg);
	
	//alert ("sending: " + string);
	
	var req = new XMLHttpRequest();
	req.open('POST', './handler.py', false);
	req.setRequestHeader('Content-Type', 'text/plain; encoding=UTF-8');
	//req.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
	//req.setRequestHeader("X-Foo", "Bar");
	req.send(string);
	
	//alert (req.responseText);
	
	msg_in = JSON.parse (req.responseText);
	parseCommands (msg_in);
	
	
	//alert (msg.toString ());
}

/** Odešle stav objektů na server. */
function sendState () {
	message = [];
	for (var i in g_components) {
		//alert ("sendState i = " + i.toString ());
		var component = g_components [i];
		var state = component.getState ();
		
		//alert ("sendState post getState");
		
		if (state != null) {
			message.push (["state", component.id, state]);
		}
	}
	
	for (var i in g_call_queue) {
		message.push (g_call_queue [i]);
	}
	
	g_call_queue = [];
	
	sendMessage (message);
}

function commandCreate (cls, id) {
	var component = new g_ctors [cls] (id);
}

function commandCall (id, fname, args) {
	var component = g_components[id];
	
	// Pokud je komponenta ve stromu, muzeme volat funkce
	if (component.has_joined_document) {
		component[fname] (args);
	}
	else {
		// Jinak pridame volani do fronty...
		component.call_queue.push ([fname, args]);
	}
}

function commandFileOut (key) {
	var wnd = window.open ("./handler.py?download="+key, "file_out");
}

function parseCommand (cmd) {
	var command = cmd[0];
	
	if (command == "create") {
		commandCreate (cmd[1], cmd[2]);
	}
	else if (command == "call") {
		commandCall (cmd[1], cmd[2], cmd[3]);
	}
	else if (command == "alert") {
		alert (cmd[1]);
	}
	else if (command == "file_out") {
		commandFileOut (cmd[1]);
	}
}

function parseCommands (commands) {
	for (var i in commands) {
		var cmd = commands [i];
		parseCommand (cmd);
	}
}

function clearElement(e) {
	while(e.firstChild != null) {
		e.removeChild(e.firstChild);
	}
}

// Vytvori uploadovaci formular
function uploadBuild () {
	/*var uframe = document.getElementById("__upload__.frame");
	var udoc = uframe.contentDocument;
	
	var uform = udoc.createElementNS(htmlns, "form");
	
	uform.setAttribute ("enctype","multipart/form-data");
	uform.setAttribute ("action","./handler.py");
	uform.setAttribute ("method", "POST");
	uform.id = "__upload__.form";
	
	var ufile = udoc.createElementNS(htmlns, "input");
	ufile.setAttribute ("type", "file");
	ufile.setAttribute ("name", "upload");
	var usubmit = udoc.createElementNS(htmlns, "input");
	usubmit.setAttribute ("type", "button");
	var ucancel = udoc.createElementNS(htmlns, "cancel");
	ucancel.setAttribute ("type", "button");*/
	
}

function onUploadSend() {
	alert("onUploadSend");
}

function onUploadCancel() {
	alert("onUploadCancel");
}
