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
LANG=C.UTF-8 FLASK_DEBUG=1 FLASK_APP=inomotior.py flask run
```

To debug-run windows:
```
set LANG=C.UTF-8
set FLASK_DEBUG=1
set FLASK_APP=inomonitor.py
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

To add an url use this command
```
flask add_url "url" "testcaseid"

```

where:

* url - url to website without protocol domain.tld NOT http(s)://domain.tld
* testcaseid - 1 - https, 2 - http

## Remove url via command line

To remove an url use this command
```
flask remove_url "url"

```

where:

* url - url to website without protocol domain.tld NOT http(s)://domain.tld

## Update url via command line

To update an url use this command
```
flask update_url "url_old" "url_new"

```

where:

* url_old -  old url to website without protocol domain.tld NOT http(s)://domain.tld
* url_new -  new url to website without protocol domain.tld NOT http(s)://domain.tld

## Add test case via command line

To update the a test case for an url use this command
```
flask update_testcase "url" "testcaseid"

```

where:

* url - url to website without protocol domain.tld NOT http(s)://domain.tld
* testcaseid - 1 - https, 2 - http
