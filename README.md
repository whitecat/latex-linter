# Latex formatter

The code behind [latexformat.com](https://latexformat.com): paste LaTeX or upload a `.tex` file and get it back
formatted by [latexindent.pl](https://github.com/cmhughes/latexindent.pl) 4.0.3, which is bundled in `latexindent/`.

This is a Python 3 rewrite (2026) of the original 2017 Flask app by
[digorithm](https://github.com/digorithm/latex-linter). It keeps the original pages, but drops the database and
the login pages, and it no longer saves a copy of what people format: each request runs in a temporary
directory that is deleted afterwards.

## Formatting options

The page sends plain form fields. The server checks each one against fixed choices and writes latexindent's
settings file itself (`-l`), so visitors can't pass their own YAML or command-line switches.

| Form field | latexindent setting |
|---|---|
| `spaces_or_tabs`, `number_of` (1–16 spaces per level) | `defaultIndent` |
| `align_ampersands` (on by default) | `lookForAlignDelims` (every environment off when unchecked) |
| `indent_document` | `noAdditionalIndent: document: 0` |
| `indent_preamble` | `indentPreamble: 1` |
| `indent_headings` | `indentAfterHeadings` for all levels, plus `indentRules` for `chapter`/`section`, whose defaults are one space |
| `wrap_columns` (0 = off, up to 500) | `-m`, `textWrapOptions: columns` |
| `one_sentence_per_line` | `-m`, `oneSentencePerLine: manipulateSentences` (and `textWrapSentences` when wrapping) |
| `condense_blank_lines` | `-m`, `condenseMultipleBlankLinesInto` |

With `indent_headings`, latexindent indents the last heading's text on into `\end{document}`, so the app moves
that line back to the start.

## Running it

```bash
mkdir -p logs && sudo chown 10001 logs   # the app runs as uid 10001 and writes logs/access.log
docker compose up -d --build
```

Then open http://localhost:8000. The image is `python:3.13-slim` with perl, `File::HomeDir` and `YAML::Tiny`
(what latexindent needs beyond core perl), Flask and gunicorn. `gunicorn.conf.py` writes the access log in Apache
combined format and takes the client address from Cloudflare's `CF-Connecting-IP` header when present.

latexindent runs with a 90-second timeout (large files can take close to a minute), under Cloudflare's 100-second
limit for proxied requests.

## Endpoints

- `POST /format/`: form field `latex_data` plus the options above; returns the formatted text.
- `POST /formatfile/`: multipart upload in `file` plus the options above; returns the formatted text.

## Licenses

The app is MIT (see `LICENSE`, from the original project's template). latexindent.pl is GPL-3.0 and copyright
Chris Hughes; see `latexindent/README` and the
[latexindent.pl repository](https://github.com/cmhughes/latexindent.pl).
