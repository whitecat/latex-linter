FROM python:3.13-slim

# Perl modules latexindent.pl 4.0.3 needs beyond core perl: File::HomeDir, YAML::Tiny
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      perl libfile-homedir-perl libyaml-tiny-perl \
 && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir flask==3.1.2 gunicorn==23.0.0

WORKDIR /app
COPY latexformat.py gunicorn.conf.py ./
COPY templates templates
COPY static static
COPY latexindent latexindent

# File::HomeDir needs a home directory. /app/logs is mounted from the host for AWStats.
RUN useradd --create-home --uid 10001 app && mkdir /app/logs && chown app /app/logs
USER app

EXPOSE 8000
CMD ["gunicorn", "latexformat:app"]
