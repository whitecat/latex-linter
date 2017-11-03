# Running the app

- Make sure you installed the python dependencies by running `pip install -r requirements.txt`
- Install the perl dependencies needed to run the latex linter perl script
  - `perl -MCPAN -e 'install "Unicode::GCString module"'`
  - `perl -MCPAN -e 'install "File::HomeDir"'`
- Run `rm -r migrations/; python manage.py create_db && python manage.py db init && python manage.py db migrate && python manage.py runserver`
