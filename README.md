[![CodeQL](https://github.com/Bwc9876/CodeReview/actions/workflows/codeql-analysis.yml/badge.svg)](https://github.com/Bwc9876/CodeReview/actions/workflows/codeql-analysis.yml)
[![Tests](https://github.com/Bwc9876/CodeReview/actions/workflows/main.yml/badge.svg)](https://github.com/Bwc9876/CodeReview/actions/workflows/main.yml)
[![Test coverage](https://raw.githubusercontent.com/Bwc9876/CodeReview/master/coverage.svg)](https://github.com/Bwc9876/CodeReview/actions/workflows/main.yml)
<a href="https://github.com/psf/black"><img alt="Code style: black" src="https://img.shields.io/badge/code%20style-black-000000.svg"></a>

# CodeReview

Code Review Workflow for IT Programming at BCTC West

## Abstract

### Flow

Through this web interface, students will be able to request code reviews and enter them into a bounty-like system.
Seniors will then be notified of this post and a senior can claim a review. After the review has concluded the senior
then fills out a rubric and enters their additional notes/comments. Finally, the instructor will then be able to take
that data and enter the grades into another grading system accordingly.

## Technical

Using ActiveDirectory, users will log in to post a request for reviews, on posting an email will be sent to seniors and
the instructor. Once a senior accepts the review, the instructor will receive an email. Upon completion of the code
review, the instructor will get a final email with the notes the senior has given.

## Help

For information on setting up and using the app, go to the [wiki](https://github.com/Bwc9876/CodeReview/wiki)
