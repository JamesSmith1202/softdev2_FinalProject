#!/usr/bin/python
import sys, os
sys.path.insert(0,"/var/www/lens/")
from lens import app as application
os.system("chown www-data:www-data www/lens/lens/data/")
os.system("chown www-data:www-data www/lens/lens/data/lens.db")
