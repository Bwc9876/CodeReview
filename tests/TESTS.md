# Intro

This document outlines the tests that are run to verify the functionality of the CodeReview tool.

## Organization

Tests are split up into separate files based on their category.  
Then, they are split up into test cases in which various cases are tested to ensure functionality.

There also exists [testing_base.py](testing_base.py) which is used as a base for all test cases.

## Coverage

Code coverage is a tool that is used to determine the percentage of code that is covered by tests. The current coverage
can be viewed in [README.md](https://github.com/Bwc9876/CodeReview/README.md). You can also view coverage by running the
following command:

```shell
$ coverage run
```

# Test Cases

## [test_auth.py](test_auth.py)

This file contains tests for the authentication module.

### LogoutTest

This test case is used to test the logout functionality.

#### test_logout

Login as a user and then logout.  
Expected result: The user is redirected to the login page.

### LDAPAuthTest

This test case is used to test the LDAP authentication module.

It creates several fake users to test authentication. It also uses fake LDAP servers to test authentication, located
in [ldap_test_server](ldap_test_server).

#### test_admin_login

Tests to see if an admin user (an instructor) can login.  
Expected result: The admin user is created in the database and the user is redirected to the main page.

#### test_student_am_login

Tests to see if a student user (specifically an AM student) can log in.  
Expected result: The AM student user is created in the database and the user is redirected to the main page.

#### test_student_pm_login

Test to see if a student user (specifically a PM student) can log in.  
Expected result: The PM student user is created in the database and the user is redirected to the main page.

#### test_has_empty

Test to make sure the authentication module can handle empty LDAP fields. Expected result: The user is created in the
database and the user has empty fields instead of `[]`.

#### test_changed

Test to make sure a user's information is updated when the user logs in even if they already are in our database.
Expected result: The user is updated in the database.

#### test_no_user

Test to make sure if an invalid id is passed, no user is returned Expected result: No user is returned

#### test_no_email

Test to make sure the user is redirected to the setup page if the user has no email. Expected result: The user is
redirected to the setup page.

#### test_invalid

Test to make sure a user is not created if the user's information is invalid. Expected result: The user is not created
in the database, and an error is shown.

#### test_cant_connect

Test to make sure an error is shown if the LDAP server cannot be connected to. Expected result: An error is shown that
informs the user the server cannot be connected to.

### UserCleanupTest

Test the user cleanup functionality.

#### test_cleanup_users

Test to make sure the user cleanup functionality works. Expected result: All users not found in the LDAP server are
deleted from the database.

#### test_no_password

Test to make sure the user cleanup functionality shows an error if the user passed no password. Expected result: An
error is shown that informs the user to enter a password.

#### test_password_wrong

Test to make sure the user cleanup functionality shows an error if the user entered the wrong password. Expected result:
An error is shown that informs the user to enter the correct password.

#### test_insufficient_perms

Test to make sure the user cleanup functionality shows an error if the user does not have sufficient permissions.
Expected result: An error is shown that informs the user that they lack permissions.

#### test_cant_connect

Test to make sure an error is shown if the LDAP server cannot be connected to. Expected result: An error is shown that
informs the user the server cannot be connected to.

## [test_email.py](test_email.py)

Test cases for emailing users.

### TestEmail

Test the email functionality.

#### test_created

Test to make sure an email is sent to reviewers when a code review is requested Expected result: An email is sent to the
reviewers

#### test_claimed

Test to make sure an email is sent to instructors when a code review is claimed Expected result: An email is sent to the
instructors

#### test_completed

Test to make sure an email is sent to instructors when a code review is completed Expected result: An email is sent to
the instructors

#### test_session_checks

Test to make sure an email is only sent to reviewers in the same session as the student Expected result: An email is
sent to the PM reviewers only

#### test_not_self

Test to make sure an email is not sent to the student when a code review is requested Expected result: An email is not
sent to the student

#### test_no_notification

Test to make sure an email is not sent to anyone who has opted out of notifications Expected result: An email is not
sent to the user who has opted out of notifications

## [test_instructor.py](test_instructor.py)

Test cases for instructor functionality.

### ListPageAccessTest

Test to make sure students can't access the instructor pages.

#### test_access

Test to make sure students can't access the instructor pages. Expected result: The user is given a 403 error.

### HomeViewTest

Test the instructor home page.

#### test_redirect

Test to make sure students can't access the instructor home page. Expected result: The user is given a 403 error.

#### test_ongoing

Test to make sure the instructor home page shows the ongoing reviews. Expected result: The instructor home page shows
the ongoing reviews.

#### test_ongoing_pm

Test to make sure the instructor home page shows the ongoing reviews for the PM session. Expected result: The instructor
home page shows the ongoing reviews for the PM session.

#### test_completed

Test to make sure the instructor home page shows the completed reviews. Expected result: The instructor home page shows
the completed reviews.

#### test_completed_overflow

Test to make sure the instructor home page has a "Show More" button when there are more than 10 completed reviews.
Expected result: The instructor home page has a "Show More" button.

#### test_completed_pm

Test to make sure the instructor home page shows the completed reviews for the PM session. Expected result: The
instructor home page shows the completed reviews for the PM session.

### UserDesignationTest

Test the user designation functionality.

#### test_designate_reviewer

Test to make sure the user can be designated as a reviewer. Expected result: reviewer-am and student-am are reviewers,
reviewer-pm and student-pm aren't.

#### test_delete_users

Test to make sure users can be deleted through the deleted checkboxes. Expected result: The users are deleted.

#### test_delete_pm

Test to make sure users can be deleted through the deleted checkboxes for the PM session. Expected result: The users are
deleted.

#### test_no_reviewers

Test to make sure passing an empty list of reviewers doesn't cause an error. Expected result: No error is thrown.

#### test_user_doesnt_exist

Test to make sure passing a user that doesn't exist shows an error. Expected result: An error is shown.

#### test_reviewers_invalid_uuid

Test to make sure passing an invalid UUID shows an error. Expected result: An error is shown.

#### test_delete_invalid_uuid

Test to make sure passing an invalid UUID shows an error. Expected result: An error is shown.

## [test_misc.py](test_misc.py)

### UserSetupTest

Test the user setup functionality.

#### test_redirects

Test to make sure the user is redirected to the setup page if they have no email. Expected result: The user is
redirected to the setup page.

#### test_admin_edit

Test to make sure the admin can edit their email. Expected result: The admins email has changed.

#### test_user_edit

Test to make sure the user can edit their email. Expected result: The users email has changed.

#### test_student_length_check

Test to make sure the length of the id the student enters is checked. Expected result: The user is given an error.

#### test_less_than_100_but_still_over_0

Test to make if a user enters a number less than 100 but still over 0, it passes validation . Expected result: The user
is not given an error.

#### test_student_numeric_check

Test to make sure the student id is numeric. Expected result: The user is given an error.

#### test_student_decimal_check

Test to make sure the student id is not a decimal. Expected result: The user is given an error.

#### test_student_negative_check

Test to make sure the student id is not a negative number. Expected result: The user is given an error.

### TestErrors

Test the error pages

#### test_404

Test to make sure the 404 page is shown. Expected result: The 404 page is shown.

#### test_403

Test to make sure the 403 page is shown. Expected result: The 403 page is shown.

#### test_500

Test to make sure the 500 page is shown. Expected result: The 500 page is shown.

#### test_500_func

Test to make sure the 500 view function works Expected result: The 500 page is shown.

#### test_404_post

Test to make sure the 404 page is shown when a post request is made. Expected result: The 404 page is shown.

#### test_403_post

Test to make sure the 403 page is shown when a post request is made. Expected result: The 403 page is shown.

#### test_500_post

Test to make sure the 500 page is shown when a post request is made. Expected result: The 500 page is shown.

#### test_invalid_type

Test to make sure the 404 page is shown when an invalid error type is given.

## [test_model_methods.py](test_model_methods.py)

### UserMethodsTest

Test the methods on the the `User` model.

#### test_user_session_str

Test to make sure the `session_from_str` method works. Expected result: The session string is returned.

#### test_user_str

Test to make sure the `__str__` method works. Expected result: The admins username is returned because they have no
name, and the user's full name is returned.

### RubricMethodsTest

Test the methods on the `Rubric` model.

#### test_rubric_str

Test to make sure the `__str__` method works. Expected result: The rubric's name is returned.

### ValUUIDTest

Test to make sure UUID validation works.

#### test_valid

Test to make sure a valid UUID is returned. Expected result: The UUID is returned.

#### test_invalid

Test to make sure an invalid UUID results in `None` being returned. Expected result: `None` is returned.

### BaseModelMethodsTest

Test the methods on the `BaseModel` model.

#### test_max_length

Test to make sure the `max_length` method works. Expected result: The max length of the `schoology_id` is returned.

### ReviewMethodsTest

Test the methods on the `Review` model.

#### test_score_fraction

Test to make sure the `score_fraction` method works. Expected result: The fraction of the score of the review is
returned.

#### test_score_fraction_not_complete

Test to make sure the `score_fraction` method returns `None` when the review is not complete. Expected result: `None` is
returned.

#### test_str

Test to make sure the `__str__` method works. Expected result: "Review From Test Student" is returned.

#### test_get_status_from_str

Test to make sure the `get_status_from_string` method works. Expected result: The status of the review ("Open", "Taken",
or "Completed")  is returned.

## [test_review.py](test_review.py)

### ReviewAccessTest

#### test_create

Test to make sure only students/reviewers can create reviews. Expected result: only students/reviewers can create
reviews.

#### test_edit

Test to make sure only the student that created the review can edit it. Expected result: only the student that created
the review can edit it.

#### test_cancel

Test to make sure only the student that created the review can cancel it. Expected result: only the student that created
the review can cancel it.

#### test_delete

Test to make sure only the instructor can delete reviews Expected result: only the instructor can delete reviews

#### test_claim

Test to make sure only reviewers in the same session can claim reviews Expected result: only reviewers in the same
session can claim reviews

#### test_abandon

Test to make sure only the reviewer that claimed the review can abandon it Expected result: only the reviewer that
claimed the review can abandon it

#### test_grade

Test to make sure only the reviewer that claimed the review can grade it Expected result: only the reviewer that claimed
the review can grade it

#### test_view

Test to make sure only users affiliates with the review (user-affiliated, reviewer-affiliated, and admin) can view it
after it had been completed Expected result: Only those users can view the review

### HomeListTest

Test the `HomeList` view.

#### test_open

Test to make sure open reviews are shown Expected result: open reviews are shown

#### test_open_different_sessions

Test to make sure open reviews aren't shown if they're in different sessions Expected result: open reviews aren't shown
if they're in different sessions

#### test_assigned

Test to make sure assigned reviews are shown Expected result: assigned reviews are shown

#### test_closed

Test to make sure closed reviews are shown Expected result: closed reviews are shown

### CompleteListTest

Test the list of completed reviews.

#### test_access

Test to make sure only reviews in this session are shown Expected result: only reviews in this session are shown

#### test_pagination

Test to make sure pagination works on the completed reviews page Expected result: pagination works on the completed
reviews page

#### test_instructor_view

Test to make sure the instructor can change sessions Expected result: the instructor can change sessions

#### test_bad_session

Test to make sure the instructor can't change sessions to a bad session Expected result: the instructor can't change
sessions to a bad session
