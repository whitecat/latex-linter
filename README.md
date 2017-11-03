# Running the app

- Make sure you installed the python dependencies by running `pip install -r requirements.txt`
- Install the perl dependencies needed to run the latex linter perl script
  - `perl -MCPAN -e 'install "Unicode::GCString module"'`
  - `perl -MCPAN -e 'install "File::HomeDir"'`
- Run `rm -r migrations/; python manage.py create_db && python manage.py db init && python manage.py db migrate && python manage.py runserver`


# Deploying using Apache

- Move the `latex-linter` folder to `/var/www`
- Create a file `/etc/apache2/sites-available/latex-linter.conf` with the following content
```
<VirtualHost *:80>
		ServerName <your domain> 
		ServerAdmin admin@mywebsite.com
		WSGIScriptAlias / /var/www/latex-linter/latex-linter.wsgi
		<Directory /var/www/latex-linter/latex-linter/>
			Order allow,deny
			Allow from all
		</Directory>
		Alias /static /var/www/latex-linter/latex-linter/project/client/static
		<Directory /var/www/latex-linter/latex-linter/project/client/static/>
			Order allow,deny
			Allow from all
		</Directory>
		ErrorLog ${APACHE_LOG_DIR}/error.log
		LogLevel warn
		CustomLog ${APACHE_LOG_DIR}/access.log combined
</VirtualHost>
```
- Restart the apache `service apache2 restart`


# Common problems

- The Perl dependencies can be a real pain to handle. If you're getting an error after installing a Perl module saying `Make not ok`, then try installing `apt-get install build-essential autoconf automake libtool gdb`, that will probably fix the build error. 
- If some of your Perl dependencies is failing, try installing the module `cpan YAML::tiny`
