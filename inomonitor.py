from flask import g
from flask import Flask
from flask import render_template, redirect
from flask import request
from flask import send_file
from functools import wraps
from flask_babel import Babel, gettext
import postgresql
import filters
from flaskext.markdown import Markdown
from markdown.extensions import Extension
from datetime import date, time, datetime
from flask_language import Language, current_language
import gettext
import click
import re
import os
import requests
from smtplib import SMTP_SSL as SMTP
from socket import gaierror

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = postgresql.open(app.config.get("DATABASE"), user=app.config.get("USER"), password=app.config.get("PASSWORD"))
    #db.row_factory = sqlite3.Row
    return db

app = Flask(__name__)
app.register_blueprint(filters.blueprint)
babel = Babel(app)
lang = Language(app)
gettext.install('motion')

class EscapeHtml(Extension):
    def extendMarkdown(self, md, md_globals):
        del md.preprocessors['html_block']
        del md.postprocessors['raw_html']
        del md.inlinePatterns['html']

md = Markdown(app, extensions=[EscapeHtml()])

class default_settings(object):
    COPYRIGHTSTART="2021"
    COPYRIGHTNAME="WPIA"
    COPYRIGHTLINK="https://wpia.club"
    IMPRINTLINK="https://documents.wpia.club/imprint.html"
    DATAPROTECTIONLINK="https://documents.wpia.club/data_privacy_policy_html_pages_en.html"

# Load config
app.config.from_object('inomonitor.default_settings')
app.config.from_pyfile('config.py')

@babel.localeselector
def get_locale():
    return str(current_language)

@lang.allowed_languages
def get_allowed_languages():
    return app.config['LANGUAGES'].keys()

@lang.default_language
def get_default_language():
    return 'en'

def get_languages():
    return app.config['LANGUAGES']

def rel_redirect(loc):
    r = redirect(loc)
    r.autocorrect_location_header = False
    return r

# Manually add vote options to the translation strings. They are used as keys in loops.
TRANSLATION_STRINGS = {_('good'), _('false')}

@app.context_processor
def init_footer_variables():
    if int(app.config.get("COPYRIGHTSTART"))<datetime.now().year:
        version_year = "%s - %s" % (app.config.get("COPYRIGHTSTART"), datetime.now().year)
    else:
        version_year = datetime.now().year

    return dict(
        footer = dict( version_year=version_year, 
            copyright_link=app.config.get("COPYRIGHTLINK"),
            copyright_name=app.config.get("COPYRIGHTNAME"),
            imprint_link=app.config.get("DATAPROTECTIONLINK"),
            dataprotection_link=app.config.get("DATAPROTECTIONLINK")
        )
    )
    
@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():
    with app.app_context():
        db = get_db()
        try:
            ver = db.prepare("SELECT version FROM schema_version")()[0][0];
            print("Database Schema version: ", ver)
        except postgresql.exceptions.UndefinedTableError:
            g._database = None
            db = get_db()
            ver = 0

        if ver < 1:
            with app.open_resource('sql/schema.sql', mode='r') as f:
                db.execute(f.read())
            return

init_db()

def check_url(url, id):
    testcaseid = 1
    try:
        response = requests.head(url, timeout=5, verify=os.path.join('certs', "ca-bundle.pem"))
        status_code = response.status_code
        reason = response.reason
    except requests.exceptions.ConnectionError as e:
        status_code = '000'
        reason = 'ConnectionError'
        print("Connection Error for " + url + ": " + e)
    good_results = [200, 403]
    result = "false"
    if int(status_code) in good_results :
        result = "good"
    db = get_db()
    message = None
    with db.xact():
        rv = db.prepare("SELECT testresult FROM testresult WHERE website_id = $1 ORDER BY entered DESC LIMIT 2")(id)
        if len(rv) == 2:
            if result == "false" and rv[0]["testresult"] == "false" and rv[1]["testresult"] == "good":
                message = "Problems with url '%s'" % url
        db.prepare("INSERT INTO testresult(\"website_id\", \"testcase_id\", \"testresult\", \"status_code\", \"response_message\") VALUES($1, $2, $3, $4, $5)")(id, testcaseid, result, int(status_code), reason)
    return message

def check_urls():
    q = "SELECT website_id, url FROM website WHERE website.deleted IS NULL"
    websites = get_db().prepare(q)
    message = None
    for website in websites:
        m = check_url( "https://" + website["url"], website['website_id'])
        if m is not None:
            if message is None:
                message = m + "\n\r"
            else:
                message += m + "\n\r"
    if message is not None:
        message = "Hi,\n\rthe WPIA Monitor reports the following problems:\n\r\n\r" + message
        email_alert(message)

def email_alert(message):
    try:
        #send your message with credentials specified above
        with SMTP(app.config.get("SMTPHOST"), app.config.get("SMTPORT")) as server:
            server.login(app.config.get("SMTPUSER"), app.config.get("SMTPPW"))
            server.sendmail(app.config.get("SMTPUSER"), app.config.get("RECIEVER"), "Subject:WPIA Monitor Alert \r\n" + message)
        # tell the script to report if your message was sent or which errors need to be fixed 
        print('Alert sent')
    except (gaierror, ConnectionRefusedError):
        print('Failed to connect to the server. Bad connection settings?')
        print("Server: " + smtp_server)
        print("Port:" + port)
    except smtplib.SMTPServerDisconnected:
        print('Failed to connect to the server. Wrong user/password?')
    except smtplib.SMTPException as e:
        print('SMTP error occurred: ' + str(e))


@app.route("/")
def main():
    if app.debug:
        check_urls()

    q = "SELECT distinct on (url) url, r.website_id, r.testresult as current_status, max(r.entered) as datestamp FROM website, testresult as r WHERE website.website_id = r.website_id AND website.deleted IS NULL GROUP BY url, r.testresult, r.website_id ORDER BY url, datestamp DESC"
    urls = get_db().prepare(q)()

    return render_template('index.html', urls = urls,
                           languages=get_languages())

@app.route("/url/<string:id>")
def url(id):
    q = "SELECT url FROM website WHERE website_id = $1"
    url = get_db().prepare(q)(int(id))
    if len(url) == 0:
        return _('Error, url not found.'), 400
    q = "SELECT r.testresult as current_status, r.entered, r.status_code, r. response_message"\
        + " FROM testresult as r WHERE r.testresult <> 'good' "\
        + " AND r.website_id = $1 ORDER BY r.entered DESC LIMIT 100 "
    results = get_db().prepare(q)(int(id))


    return render_template('single_domain.html', url = url[0][0], results = results, resultcount = len(results),
                           languages=get_languages())

@app.route("/language/<string:language>")
def set_language(language):
    lang.change_language(language)
    return rel_redirect("/")

# commandline functions
@app.cli.command("check")
def check_job():
    check_urls()

@app.cli.command("add_url")
@click.argument("url")
def add_url(url):
    db = get_db()
    with db.xact():
        rv = db.prepare("SELECT url FROM website WHERE lower(url)=lower($1)")(url)
        messagetext = _("URL '%s' already exists .") % (url)
        if len(rv) == 0:
            db.prepare("INSERT INTO website(\"url\") VALUES($1)")(url)
            messagetext = _("URL '%s' inserted.") % (url)
    click.echo(messagetext)
