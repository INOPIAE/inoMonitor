# WPIA Website monitor

The WPIA mointor is a small application to monitor websites.

# Installation
Requires Python 3 and a running PostgreSQL installation.

For a productive environment use a nginx webserver.


To install:

```
virtualenv -p python3 .
. bin/activate
pip install -r requirements.txt
```
Then edit config.py.example into config.py with your database connection and smtp settings.

Configure a cron job that calls the user api function check_job e.g.every 10 minutes.

## Development and debug

To debug-run linux:

```
LANG=C.UTF-8 FLASK_DEBUG=1 FLASK_APP=motion.py flask run
```

To debug-run windows:
```
set LANG=C.UTF-8
set FLASK_DEBUG=1
set FLASK_APP=motion.py
flask run
```

For unit testing use config values from config.py.example:
```
python -m unittest tests/test_motion.py
```

The database schema is automatically installed when the table "schema_version" does not exist and the application is started.

# Command line functions

For linux start with
```
FLASK_APP=motion.py
```

For windows start with
```
set FLASK_APP=motion.py

```

## Start check via command line

To start a check eg. for a cronjob use this command
```
flask check

```


## Add url via command line

To add a user use this command
```
flask add_url "url"

```

where:

* url - url to website without protocol domain.tld NOT http(s)://domain.tld
