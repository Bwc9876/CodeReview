from uuid import uuid4

from django.urls import reverse

from Main.models import Review
from Users.models import User
from tests.testing_base import BaseCase, SimpleBaseCase


class ListPageAccessTest(SimpleBaseCase):
    test_admin = True

    test_users = BaseCase.USER_SINGLE_STUDENT

    urls = ['instructor-home', 'user-list', 'rubric-list']

    def test_access(self):
        for url in self.urls:
            response = self.get('test-user', reverse(url))
            self.assertEqual('errors/403.html', response.template_name[0])
            response = self.get('super', reverse(url))
            self.assertEqual(response.status_code, 200)


class HomeViewTest(BaseCase):
    test_users = BaseCase.USER_STUDENT_REVIEWER

    test_review_student = 'student'
    test_review_reviewer = 'reviewer'

    def test_redirect(self) -> None:
        self.post('super', reverse('user-setup', kwargs={'pk': self.users['super'].id}), {'email': "admin"})
        response = self.clients['super'].get(reverse('home'))
        self.assertRedirects(response, reverse('instructor-home'))

    def test_ongoing(self) -> None:
        self.set_test_review_status(Review.Status.ASSIGNED)
        response = self.get('super', reverse('instructor-home'))
        self.assertIn(self.review, response.context.get('am_active', []))

    def test_ongoing_pm(self) -> None:
        self.set_user_session('student', User.Session.PM)
        self.set_test_review_status(Review.Status.ASSIGNED)
        response = self.get('super', reverse('instructor-home'))
        self.assertIn(self.review, response.context.get('pm_active', []))

    def test_completed(self) -> None:
        self.set_test_review_status(Review.Status.ASSIGNED)
        self.post_test_review('reviewer', 'review-grade', {'scores': "[10,2]"})
        response = self.get('super', reverse('instructor-home'))
        self.assertIn(self.review, response.context.get('am_completed', []))

    def test_completed_overflow(self) -> None:
        for x in range(5):
            new_review = self.make_arb_review('student', 'reviewer', Review.Status.ASSIGNED, f"12.34.0{x}")
            self.post_review('reviewer', 'review-grade', new_review.id, {'scores': "[10,2]"})
        response = self.get('super', reverse('instructor-home'))
        self.assertIn("review/completed/?session=AM", str(response.content))

    def test_completed_pm(self) -> None:
        self.set_user_session('student', User.Session.PM)
        self.set_test_review_status(Review.Status.ASSIGNED)
        self.post_test_review('reviewer', 'review-grade', {'scores': "[10,2]"})
        response = self.get('super', reverse('instructor-home'))
        self.assertIn(self.review, response.context.get('pm_completed', []))


class UserDesignationTest(BaseCase):
    url = reverse('user-list')

    test_users = BaseCase.USER_AM_PM

    test_review = False
    test_rubric = False

    def make_reviewers_list(self, user_list):
        return [str(self.users[user].id) for user in user_list]

    def post_list(self, reviewers=None, delete=None):
        if reviewers is None:
            reviewers = []
        if delete is None:
            delete = []
        self.post('super', reverse('user-list'), data={
            'reviewers': self.make_reviewers_list(reviewers),
            'to_delete': self.make_reviewers_list(delete)
        })

    def test_designate_reviewer(self) -> None:
        self.post_list(reviewers=['reviewer-am', 'student-am'])
        self.assertReviewer('reviewer-am')
        self.assertNotReviewer('reviewer-pm')
        self.assertReviewer('student-am')
        self.assertNotReviewer('student-pm')

    def test_delete_users(self) -> None:
        self.post_list(delete=['reviewer-am', 'student-am'])
        self.assertUserDoesNotExist('reviewer-am')
        self.assertUserDoesNotExist('student-am')
        self.assertUserExists('reviewer-pm')

    def test_delete_pm(self) -> None:
        self.post_list(delete=['reviewer-pm', 'student-am'])
        self.assertUserDoesNotExist('reviewer-pm')
        self.assertUserDoesNotExist('student-am')
        self.assertUserExists('reviewer-am')

    def test_no_reviewers(self) -> None:
        self.post_list()
        self.assertNotReviewer('reviewer-am')
        self.assertNotReviewer('reviewer-pm')
        self.assertNotReviewer('student-am')
        self.assertNotReviewer('student-pm')

    def test_user_doesnt_exist(self) -> None:
        self.post('super', reverse('user-list'), data={
            'reviewers': self.make_reviewers_list(['reviewer-am']) + [str(uuid4())],
            'to_delete': self.make_reviewers_list(['student-am']) + [str(uuid4())]
        })
        self.assertReviewer('reviewer-am')
        self.assertUserDoesNotExist('student-am')

    def test_reviewers_invalid_uuid(self) -> None:
        response = self.post('super', reverse('user-list'), data={
            'reviewers': ["bad-uuid"], 'to_delete': []
        })
        self.assertMessage(response, "Invalid User IDs")

    def test_delete_invalid_uuid(self) -> None:
        response = self.post('super', reverse('user-list'), data={
            'reviewers': self.make_reviewers_list(["reviewer-am", "reviewer-pm"]), 'to_delete': ["bad-uuid"]
        })
        self.assertMessage(response, "Invalid User IDs")
