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
$ coverage report
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

Tests to see if an admin user (an instructor) can log in.  
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

Test to make sure if an invalid id is passed, no user is returned. Expected result: No user is returned

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

Test to make sure an email is sent to reviewers when a code review is requested. Expected result: An email is sent to
the reviewers

#### test_claimed

Test to make sure an email is sent to instructors when a code review is claimed. Expected result: An email is sent to
the instructors

#### test_completed

Test to make sure an email is sent to instructors when a code review is completed. Expected result: An email is sent to
the instructors

#### test_session_checks

Test to make sure an email is only sent to reviewers in the same session as the student. Expected result: An email is
sent to the PM reviewers only

#### test_not_self

Test to make sure an email is not sent to the student when a code review is requested. Expected result: An email is not
sent to the student

#### test_no_notification

Test to make sure an email is not sent to anyone who has opted out of notifications. Expected result: An email is not
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

Test to make if a user enters a number less than 100 but still over 0, it passes validation. Expected result: The user
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

Test the methods on the `User` model.

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

Test to make sure only the instructor can delete reviews. Expected result: only the instructor can delete reviews

#### test_claim

Test to make sure only reviewers in the same session can claim reviews. Expected result: only reviewers in the same
session can claim reviews

#### test_abandon

Test to make sure only the reviewer that claimed the review can abandon it. Expected result: only the reviewer that
claimed the review can abandon it

#### test_grade

Test to make sure only the reviewer that claimed the review can grade it. Expected result: only the reviewer that
claimed the review can grade it

#### test_view

Test to make sure only users affiliates with the review (user-affiliated, reviewer-affiliated, and admin) can view it
after it had been completed Expected result: Only those users can view the review

### HomeListTest

Test the `HomeList` view.

#### test_open

Test to make sure open reviews are shown. Expected result: open reviews are shown

#### test_open_different_sessions

Test to make sure open reviews aren't shown if they're in different sessions. Expected result: open reviews aren't shown
if they're in different sessions

#### test_assigned

Test to make sure assigned reviews are shown. Expected result: assigned reviews are shown

#### test_closed

Test to make sure closed reviews are shown. Expected result: closed reviews are shown

### CompleteListTest

Test the list of completed reviews.

#### test_access

Test to make sure only reviews in this session are shown. Expected result: only reviews in this session are shown

#### test_pagination

Test to make sure pagination works on the completed reviews page. Expected result: pagination works on the completed
reviews page

#### test_instructor_view

Test to make sure the instructor can change sessions. Expected result: the instructor can change sessions

#### test_bad_session

Test to make sure the instructor can't change sessions to a bad session. Expected result: the instructor can't change
sessions to a bad session

### ReviewCreateTest

Test the creating (requesting) reviews

#### test_created

Test to make sure students can request code reviews.
Expected result: the student can request a code review

#### test_limit

Test to make sure the user can't create more than 2 reviews.
Expected result: the user gets an error

### ReviewSchoologyIDValidationTest

Test the validation of the schoology id the user enters.

#### test_too_short

Test to make sure an id that is too short is not accepted.
Expected result: the user gets an error

#### test_too_long

Test to make sure an id that is too long is not accepted.
Expected result: the user gets an error

#### test_no_dots

Test to make sure an id without any dots (.) is not accepted.
Expected result: the user gets an error

#### test_not_number

Test to make sure a schoology ID that has non-numeric components is not accepted.
Expected result: the user gets an error

#### test_negative

Test to make sure if that a schoology id with a negative number in a component is not accepted.
Expected result: the user gets an error

### ReviewCancelUnclaimedTest

Test a student's ability to cancel a review that hasn't been claimed.

#### test_cancel

Test to make sure the user can cancel the review.
Expected result: the review is cancelled

### ReviewCancelClaimedTest

Test a student's ability to cancel a review that has already been claimed.

#### test_cancel

Test to make sure the user can cancel the review.
Expected result: the review is cancelled

### ReviewEditUnclaimedTest

Test a student's ability to edit an unclaimed review

#### test_edit

Test to make sure the student can edit a review.
Expected result: The schoology id of the review is changed

### ReviewEditClaimedTest

Test a student's ability to edit a claimed review

#### test_edit

Test to make sure the student can edit a review.
Expected result: The schoology id of the review is changed

### ReviewClaimTest

Test the ability for a reviewer to claim reviews.

#### test_claim

Test to make sure a reviewer can claim reviews.
Expected result: The review is claimed by `reviewer`

#### test_claim_different_session

Test to make sure a reviewer cannot claim a review from a different session.
Expected result: the user gets a 404 error

#### test_limit

Test to make sure a reviewer cannot claim more than 2 reviews.
Expected result: the user gets an error message

### ReviewAbandonTest

Test a reviewer's ability to abandon reviews.

#### test_abandon

Test to make sure a reviewer can abandon reviews.
Expected result: the review is abandon

### ReviewGradeTest

Test a reviewer's ability to grade reviews

#### test_draft

Test to make sure a reviewer can save a draft of a review.
Expected result: the review is saved as a draft and the scores/additional comments are preserved

#### test_draft_empties

Test to make sure a reviewer can save a draft of a review with empty scores/additional comments.
Expected result: the review is saved as a draft and the scores/additional comments are preserved

#### test_draft_then_rubric_change

Test to make sure that if a student changes the rubric of an ongoing review with a draft, the draft is discarded.
Expected result: The scored rows are cleared when the rubric is changed

#### test_draft_then_rubric_no_change

Test to make sure if a student *doesn't* change the rubric of an ongoing review with a draft, the draft is preserved.
Expected result: The scored rows are preserved when the rubric is changed

#### test_grade

Test to make sure a reviewer can grade reviews.
Expected result: the review is graded with a score of 7/12

#### test_grade_not_json

Test to make sure a grade that is not JSON is denied.
Expected result: the user gets an error message

#### test_grade_non_numeric

Test to make sure a grade that contains non-numeric elements is denied.
Expected result: the user gets an error message

#### test_grade_none

Test to make sure a grade with no elements is denied.
Expected result: the user gets an error message

#### test_grade_too_many

Test to make sure a grade that has more rows than the rubric is denied.
Expected result: the user gets an error message

#### test_grade_not_scores

Test to make sure a grade that has scores that don't apply to the rubric is denied.
Expected result: the user gets an error message

#### test_grade_in_range_but_not_valid

Edge case for previous test

#### test_grade_zeroes

Test to make sure a grade with just 0s is denied.
Expected result: the user gets an error message

#### test_grade_under_limit

Test to make sure negative grades are denied.
Expected result: the user gets an error message

#### test_no_instance

Test to make sure passing no review to GradeReviewForm throws an error. Expected result: `ValueError` is thrown

### UpdateReviewScoreOnRubricEditTest

Test behaviour for when the instructor edits a rubric that an already graded review already uses.

#### test_new_rows

Test to make sure when new rows are added, reviews will have those rows marked as 0.
Expected result: the review's score stays as 12/12

#### test_delete_row

Test to make sure when a row is deleted, reviews will have those scores removed.
Expected result: the score goes down to 10/10

## [test_rubric.py](test_rubric.py)

Test the rubric functionality

### RubricFormTest

Test the creation/editing of rubric forms

#### test_access

Test to make sure students can't access the rubric form.
Expected result: the user gets a 403 error

#### test_form

Test to make sure the instructor can create a rubric through the form.
Expected result: a new rubric is created

### RubricValidationTest

All of these tests are self-explanatory, they just check to ensure rubric JSON is valid

### RubricDeleteTest

Test the ability for the instructor to delete rubrics

#### test_delete

Test to make sure a rubric can be deleted.
Expected result: The rubric no longer exists

#### test_get

Test to make sure a prompt is shown to the user when trying to delete a review.
Expected result: the user is shown a confirmation prompt

### RubricEditTest

Test the ability for an instructor to edit a rubric

#### test_edit

Test to make sure an instructor can edit a rubric.
Expected result: The rubric has changed

### RubricListTest

Test the rubric list page

#### test_access

Test to make sure students can't access the rubric list page. Expected result: the student gets a 403 error

#### test_list

Test to make sure all rubrics are shown on the rubric list page.
Expected result: the test rubric is shown on the list page

### RubricDuplicateTest

Test the instructor's ability to duplicate reviews

#### test_dupe

Test to make sure the rubric is duplicated.
Expected result: the test rubric is duplicated

#### test_invalid_id

Test to make sure the user is given an error if they pass an ID that does not exist.
Expected result: the user gets a 404 error

#### test_name_long

Test to make sure a rubric that has a very long name and is duplicated will have a shortened name.
Expected result: A new rubric called "New Rubric" is created opposed to "Test Rubric Copy"

## [test_tags.py](test_tags.py)

Test template tags

### CommonTagsTest

Test common template tags

#### test_make_spaces

Test to make sure the `make_spaces` template tag works.
Expected result: "_" and "-" are replaced with a space

#### test_get_link_class

Test to make sure the `test_get_link_class` tag works.
Expected result: the proper CSS classes are returned for the given action type

#### test_get_alert_class

Test to make sure the `test_get_alert_class` tag works. Expected result: The proper CSS class is returned for each given
alert type

#### test_get_icon_class

Test to make sure the `test_get_icon_class` tag works.
Expected result: The proper CSS icon class is returned for each alert type

### TestReviewTags

Test tags specific to reviews

#### test_session

Test to make sure the `get_session` tag works on a given review.
Expected result: "AM Session" and "PM Session" are returned properly
