# project/server/main/views.py


#################
#### imports ####
#################

from flask import render_template, Blueprint, request
import json
from .handlers import handle_latex_text, handle_latex_file

################
#### config ####
################

main_blueprint = Blueprint('main', __name__,)


################
#### routes ####
################


@main_blueprint.route('/')
def home():
    return render_template('main/home.html')


@main_blueprint.route("/about/")
def about():
    return render_template("main/about.html")


@main_blueprint.route("/format/", methods=["POST"])
def format_code():
    #TODO: be defensive here. The front end is a mess so I have to check stuff here
    # TODO: get options from the client side, build a JSON very alike to this one
    options = {}
    options["isTabs"] = False

    if request.form["spaces_or_tabs"] == "tabs":
      options["isTabs"] = True

    options["number_of"] = request.form["number_of"]

    formatted_latex = handle_latex_text(request.form["latex_data"], options)
    return formatted_latex

@main_blueprint.route("/formatfile/", methods=["POST"])
def format_file():
    latex_file = request.files['file']
    options = {}
    options["isTabs"] = False

    if request.form["spaces_or_tabs"] == "tabs":
      options["isTabs"] = True

    options["number_of"] = request.form["number_of"]

    formatted_latex = handle_latex_file(latex_file, options)

    return formatted_latex
