# latexformat.com: runs latexindent.pl on pasted or uploaded LaTeX and returns the result.
# Ported from digorithm/latex-linter (Python 2, Flask 0.12). Nothing is stored: each
# request is formatted in its own temporary directory, which is deleted afterwards.
import os
import re
import subprocess
import tempfile

from flask import Blueprint, Flask, Response, abort, redirect, render_template, request

HERE = os.path.dirname(os.path.abspath(__file__))
LATEXINDENT = os.path.join(HERE, "latexindent", "latexindent.pl")
TIMEOUT = 90  # Cloudflare drops proxied requests after 100 s

HEADINGS = ("part", "chapter", "section", "subsection", "subsection*", "subsubsection",
            "paragraph", "subparagraph")
# Environments latexindent aligns at & by default; turning alignment off has to list each one
with open(os.path.join(HERE, "latexindent", "defaultSettings.yaml"), encoding="utf-8") as f:
    _block = re.search(r"^lookForAlignDelims:\n((?:(?:  .*)?\n)+?)\S", f.read(), re.M).group(1)
ALIGN_ENVIRONMENTS = re.findall(r"^  (\S+):", _block, re.M)

app = Flask(__name__, template_folder="templates", static_folder="static")
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024

# The templates use url_for("main.home") and url_for("main.about")
main = Blueprint("main", __name__)


@app.before_request
def drop_www():
    # www.<site> redirects permanently to <site>, keeping the path and query.
    # 308 for POSTs so the form data survives; browsers turn a 301 POST into a GET.
    host = request.host
    if host.lower().startswith("www."):
        url = "https://" + host[4:] + request.full_path.rstrip("?")
        return redirect(url, code=301 if request.method in ("GET", "HEAD") else 308)


def _flag(form, name, default=False):
    value = form.get(name)
    return default if value is None else value in ("1", "on", "true")


def _number(form, name, default, low, high):
    value = form.get(name, str(default))
    if not value.isdigit() or not low <= int(value) <= high:
        abort(400)
    return int(value)


def _settings(form):
    """Build latexindent's local settings YAML from the form. Only these fixed options are
    accepted; users never supply YAML or switches. Returns (yaml, needs -m)."""
    tabs = form.get("spaces_or_tabs") == "tabs"
    spaces = _number(form, "number_of", 4, 1, 16)
    wrap = _number(form, "wrap_columns", 0, 0, 500)
    sentences = _flag(form, "one_sentence_per_line")
    condense = _flag(form, "condense_blank_lines")

    indent = "\\t" if tabs else " " * spaces
    lines = ['defaultIndent: "%s"' % indent]
    if _flag(form, "indent_preamble"):
        lines.append("indentPreamble: 1")
    if _flag(form, "indent_document"):
        lines += ["noAdditionalIndent:", "  document: 0"]
    if _flag(form, "indent_headings"):
        lines.append("indentAfterHeadings:")
        for heading in HEADINGS:
            lines += ["  %s:" % heading, "    lookForThis: 1"]
        # defaultSettings.yaml ships example one-space rules for these two
        lines += ["indentRules:", '  chapter: "%s"' % indent, '  section: "%s"' % indent]
    if not _flag(form, "align_ampersands", default=True):
        lines.append("lookForAlignDelims:")
        lines += ["  %s: 0" % env for env in ALIGN_ENVIRONMENTS]
    modify = bool(wrap or sentences or condense)
    if modify:
        # -m turns on every modifyLineBreaks feature at its default; set ours explicitly
        lines += ["modifyLineBreaks:",
                  "  condenseMultipleBlankLinesInto: %d" % condense,
                  "  oneSentencePerLine:",
                  "    manipulateSentences: %d" % sentences,
                  # otherwise one sentence per line turns wrapping off
                  "    textWrapSentences: %d" % bool(sentences and wrap),
                  "  textWrapOptions:",
                  "    columns: %d" % wrap]
    return "\n".join(lines) + "\n", modify


def _format(write_input, form):
    settings, modify = _settings(form)
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "input.tex")
        write_input(path)
        settings_path = os.path.join(tmp, "settings.yaml")
        with open(settings_path, "w", encoding="utf-8") as f:
            f.write(settings)
        # -w overwrites the file in place; indent.log and the .bak0 backup land in tmp
        command = ["perl", LATEXINDENT, "-w", "-l=" + settings_path] + (["-m"] if modify else []) + [path]
        try:
            subprocess.run(command, cwd=tmp, timeout=TIMEOUT,
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except subprocess.TimeoutExpired:
            abort(504)
        with open(path, "rb") as f:
            output = f.read()
        if _flag(form, "indent_headings"):
            # The last heading's indentation runs on into \end{document}
            output = re.sub(rb"(?m)^[ \t]+(\\end\{document\})", rb"\1", output)
        return Response(output, mimetype="text/plain")


@main.route("/")
def home():
    return render_template("main/home.html")


@main.route("/about/")
def about():
    return render_template("main/about.html")


@main.route("/format/", methods=["POST"])
def format_code():
    text = request.form.get("latex_data", "")

    def write(path):
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)
    return _format(write, request.form)


@main.route("/formatfile/", methods=["POST"])
def format_file():
    upload = request.files.get("file")
    if upload is None:
        abort(400)
    return _format(upload.save, request.form)


@app.errorhandler(404)
def page_not_found(error):
    return render_template("errors/404.html"), 404


@app.errorhandler(500)
def server_error_page(error):
    return render_template("errors/500.html"), 500


app.register_blueprint(main)
