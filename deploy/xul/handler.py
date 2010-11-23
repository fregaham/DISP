
import disp.xul
import disp.xul.launcher

import main

def handler(req):
	return disp.xul.launcher.launch (main.Main, req, "/var/www/aplikace/xul/")
