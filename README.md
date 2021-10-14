[![CodeQL](https://github.com/Bwc9876/CodeReview/actions/workflows/codeql-analysis.yml/badge.svg)](https://github.com/Bwc9876/CodeReview/actions/workflows/codeql-analysis.yml)
[![Tests](https://github.com/Bwc9876/CodeReview/actions/workflows/main.yml/badge.svg)](https://github.com/Bwc9876/CodeReview/actions/workflows/main.yml)
![Test coverage](https://github.com/Bwc9876/CodeReview/blob/master/coverage.svg)

# CodeReview

Code Review Workflow for IT Programming at BCTC West

## Abstract

### Flow

Through this web interface, students will be able to request code reviews and enter them into a bounty-like system.
Seniors will then be notified of this post and a senior can claim a review. After the review has concluded the senior
then fills out a rubric and enters their additional notes/comments. Finally, the instructor will then be able to take
that data and enter the grades into another grading system accordingly.

### UI

Basic material design layout and UI with primary, secondary, and accent colors.

## Technical

Using ActiveDirectory, users will log in to post a request for reviews, on posting an email will be sent to seniors and
the instructor. Once a senior accepts the review, the instructor will receive an email. Upon completion of the code
review, the instructor will get a final email with the notes the senior has given.

### Environment Variables

- DEV_STAGE: The current stage of development options are: Dev, Prod, and GitHub
- PRODUCTION_HOST: The host to use in the production environment
- SECRET_KEY: Key to use in production as the Django secret key
- EMAIL_HOST: The email server host we're connecting to
- EMAIL_USER: The username of the email we'll use to send notifications
- EMAIL_PASS: The password to use for the email
- DB_HOST: The host for the database we'll use (MySQL Type)
- DB_NAME: The name for the DB we'll use
- DB_PASS: The password for the DB we'll use
- LDAP_URL: The URL of the ActiveDirectory Server we want to use for auth
- LDAP_USER: The username of the LDAP admin we want to log in as
- LDAP_PASS: The password of the LDAP admin we want to log in as

### Services Used

- [Python](https://www.python.org/)
- [Django](https://www.djangoproject.com/)
- [ActiveDirectory](https://docs.microsoft.com/en-us/windows-server/identity/ad-ds/get-started/virtual-dc/active-directory-domain-services-overview)
- [lapd3](https://pypi.org/project/ldap3/)
- [Jquery](https://jquery.com/)
- [FontAwesome](https://fontawesome.com/)
- [JsonSchema](https://pypi.org/project/jsonschema/)

## Running

For both development and production, you'll need to clone the repository:

```sh
git clone https://github.com/Bwc9876/CodeReview.git
```

...And install dependencies

```sh
pip install -r requirements.txt
```

### Development

First, set up a database to test with by running:

```sh
python manage.py migrate
```

Then, you'll need to create a superuser to log in as

```sh
python manage.py createsuperuser
Username: admin
Email:       (Can be left blank)
Password: ********
Confirm Password: ********
```

Now you're ready to host the local development server by running

```sh
python manage.py runserver 127.0.0.1:8000
```

You can connect by typing "127.0.0.1:8000" in your browser

#### Note about emails

The app is set up to output all emails to the "debug-emails" folder in the project, so no emails will be sent.

### Production

Will require an SQL server to connect to, an ActiveDirectory server, an email to send notifications from, and a
webserver to run the Django code on.  
Set up your webserver and then point it to ```CodeReview/wsgi.py```.  
This will require [environment variables](#Environment-Variables)

### Tests

Tests are available through a file named run_tests.py
``` python run_tests.py ```

#### Test Coverage

To see how well tests cover the code, install coverage:

```sh
pip install coverage==6.0.2
```

Then run coverage

```sh
coverage run
```

Finally, do this to show the report

```sh
coverage report
```
