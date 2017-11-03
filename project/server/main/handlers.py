# project/server/main/handlers.py

#################
#### imports ####
#################

from flask import render_template, Blueprint, request
from project.server import db
from project.server.models import LatexFile
from werkzeug.datastructures import FileStorage
import json
import uuid
import os
import subprocess
import logging

# Global variables (disguting, I know)
# TODO: make it dynamic. I had to put /var/www here because of apache, which is quite annoying
# NOTE: If running locally and not using apache at all, change this path to make it work
latex_file_path = '/var/www/latex-linter/project/server/files/'
perl_script_path = '/var/www/latex-linter/project/server/dependencies/latexindent.pl-master/latexindent.pl'

def _generate_unique_id():
    return str(uuid.uuid4())

def _write_to_file(text):
    uuid = _generate_unique_id()
    file_path = '{}{}.tex'.format(latex_file_path, uuid)

    with open(file_path, 'w') as latex_file:
        latex_file.write(text)

    return (uuid, file_path)

def _apply_options(uuid, file_path, options):
    if options["isTabs"] == True:
        print("leave it be")
    else:
        # Convert tabs to spaces
        number_of_spaces = options["number_of"]
        tmp_file_path = "{}/{}.tmp".format(latex_file_path, uuid)
        out_file = open(tmp_file_path, 'w')
        subprocess.call(['expand', '-t',number_of_spaces, file_path], stdout=out_file)
        subprocess.call(['mv', tmp_file_path, file_path])

def _run_perl_script(latex_file):
    subprocess.call(['perl', perl_script_path, '-w', latex_file])

def handle_latex_text(latex_text, options):
    # TODO: script to install dependencies - Unicode::GCString and File::HomeDir

    latex_file = _write_to_file(latex_text)
    
    print latex_file
    # latex_file[0] == UUID & latex_file[1] == file_path
    output = _run_perl_script(latex_file[1])

    _apply_options(latex_file[0], latex_file[1], options)

    file_text = open(latex_file[1], 'r').read()

    db_latex_file = LatexFile(uuid=latex_file[0], text=file_text)

    db.session.add(db_latex_file)
    db.session.commit()

    return file_text

def handle_latex_file(latex_file, options):
    f = FileStorage(latex_file)

    uuid = _generate_unique_id()
    file_path = '{}{}.tex'.format(latex_file_path, uuid)

    f.save(file_path)

    output = _run_perl_script(file_path)
    _apply_options(uuid, file_path, options)
    file_text = open(file_path, 'r').read()

    db_latex_file = LatexFile(uuid=uuid, text=file_text)

    db.session.add(db_latex_file)
    db.session.commit()

    return file_text
