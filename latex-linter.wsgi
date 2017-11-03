#!/usr/bin/python
import sys
import logging
logging.basicConfig(stream=sys.stderr)
sys.path.insert(0,"/var/www/latex-linter/")

from project.server import app as application
application.secret_key = 'my_precious'
