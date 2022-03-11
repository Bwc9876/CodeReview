# Issues

Ask for assignment before you begin working on an issue

# Cloning
To get started with development, fork and clone the repo:
```shell
$ git clone https://github.com/YourUser/CodeReview
```
Then, create a venv and install all requirements
```shell
$ python -m venv venv
$ ./venv/scripts/activate
$ ./venv/scripts/pip install -r requirements.txt
```
Now, start the development server
```shell
$ python manage.py runserver your.ip.address:port
```

# Environment Variables
See [Environment Variables](https://github.com/Bwc9876/CodeReview/wiki/Environment-Variables) on the wiki for info on what each one does.  
Create a file called `env.ps1` and it will automatically be loaded into the env.  

# Style Guide
We try our best to adhere to PEP:
- Variables in snake_case
- Functions/Methods in snake_case
- Classes in PascalCase
- Files in snake_case
- Private Attributes use `_` or `__`

# Testing
To test your changes, run:
```shell
$ python run_tests.py
```
# Coverage
To get testing coverage, install coverage:
```shell
$ ./venv/scripts/pip install coverage
```
And then run:
```shell
$ coverage run
```
Once testing completes run:
```shell
$ coverage report
```
To get a report of code coverage  
**Code coverage should stay above 95%**

# Pull Requests

Submit a PR explaining your changes in detail. Changes will be checked for
- Style
- Functionality
- Best Practices

If your changes address an issue please use the `resolves` keyword to close it automatically

# Actions

We use CodeQL for both python and js, these checks are not run on PR.  
We also run unit tests on any PRs that target `master`, these tests must pass with >95% code coverage to be merged.

