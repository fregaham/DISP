
import disp.web
import disp.web.launcher

import main

def handler(req):
	return disp.web.launcher.launch (req, main.Main, "./index.py", "/var/www/aplikace/web/")
