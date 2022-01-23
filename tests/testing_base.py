from django.contrib.messages import get_messages
from django.test import TestCase, Client
from django.urls import reverse

from Instructor.models import Rubric
from Main.models import Review
from Users.models import User


class BadTestError(Exception):
    pass


class BaseCase(TestCase):
    # Configuration

    # "name": (is_reviewer, pm)
    test_users = {}
    test_admin = True
    test_rubric = True
    test_review = True
    test_review_student = ""
    test_review_reviewer = ""

    # Defaults

    USER_SINGLE_STUDENT = {
        'test-user': (False, False)
    }

    USER_AM_PM = {
        'reviewer-am': (True, False),
        'student-am': (False, False),
        'reviewer-pm': (True, True),
        'student-pm': (False, True)
    }

    USER_STUDENT_REVIEWER = {
        'reviewer': (True, False),
        'student': (False, False)
    }

    # Setup

    @staticmethod
    def get_test_rubric_json() -> str:
        with open("tests/test_rubric.json", 'r') as file:
            test_json = file.read()
        return test_json

    def make_test_rubric(self) -> None:
        self.clients['super'].post(reverse("rubric-create"), {'name': "Test Rubric",
                                                              'rubric': self.get_test_rubric_json()})
        self.rubric = Rubric.objects.get(name="Test Rubric")

    def make_arb_review(self, student, reviewer, status, schoology_id):
        return Review.objects.create(student=self.users[student], schoology_id=schoology_id,
                                     reviewer=self.users[reviewer], status=status, rubric=self.rubric)

    def make_test_review(self) -> None:
        self.review = Review.objects.create(rubric=self.rubric, schoology_id="12.34.56",
                                            student=self.users[self.test_review_student],
                                            reviewer=None if self.test_review_reviewer is None else self.users[
                                                self.test_review_reviewer])

    def make_arb_user(self, name, password, make_client=True):
        self.users[name] = User.objects.create_user(name, password=password)
        if make_client:
            self.clients[name] = Client()
            self.clients[name].force_login(self.users[name])

    def _create_user_matrix(self):
        self.users = {}
        for name, attrs in self.test_users.items():
            self.users[name] = User.objects.create_user(name, email=f"{name}@example.com", password=f"test-password",
                                                        is_reviewer=attrs[0],
                                                        session=User.Session.PM if attrs[1] else User.Session.AM)
        if self.test_admin:
            self.users['super'] = User.objects.create_superuser('admin', password="test-password",
                                                                email="admin@example.com")

    def _create_clients(self):
        clients = {}
        for key in self.users.keys():
            val = self.users.get(key)
            new_client = Client()
            new_client.force_login(val)
            clients[key] = new_client
        self.clients = clients

    def __new__(cls, *args, **kwargs):
        if "super" in cls.test_users.keys():
            raise BadTestError("Super is created automatically, don't include it in test_users")
        elif cls.test_review is True and cls.test_rubric is False:
            raise BadTestError("Can't make a test review without the test rubric")
        elif cls.test_review is True and cls.test_review_student not in cls.test_users.keys():
            raise BadTestError("Test review student not found in test_users")
        elif cls.test_review is True and cls.test_review_reviewer is not None and cls.test_review_reviewer not in cls.test_users.keys():
            raise BadTestError("Test review reviewer not found in test_users")
        else:
            return super(BaseCase, cls).__new__(cls)

    def setUp(self) -> None:
        self._create_user_matrix()
        self._create_clients()
        if self.test_rubric:
            self.make_test_rubric()
            if self.test_review:
                self.make_test_review()

    # Assertions

    def assertMessage(self, response, message_text):
        self.assertIn(message_text, [m.message for m in get_messages(response.wsgi_request)])

    def assertUserExists(self, username):
        self.assertTrue(User.objects.filter(username=username).exists())

    def assertUserDoesNotExist(self, username):
        self.assertFalse(User.objects.filter(username=username).exists())

    def assertReviewer(self, username):
        self.assertTrue(User.objects.get(username=username).is_reviewer)

    def assertNotReviewer(self, username):
        self.assertFalse(User.objects.get(username=username).is_reviewer)

    # Client Utils

    def get(self, user, path, data=None):
        return self.clients[user].get(path, data)

    def post(self, user, path, data=None):
        return self.clients[user].post(path, data)

    def post_review(self, user, action, review_id, data=None):
        return self.post(user, reverse(action, kwargs={'pk': review_id}), data)

    def post_test_review(self, user, action, data=None):
        return self.post_review(user, action, self.review.id, data)

    # Review Utils

    def set_test_review_status(self, new_status):
        self.review.status = new_status
        self.review.save()

    def refresh_test_review(self):
        self.review = Review.objects.get(id=self.review.id)

    # User Utils

    def set_user_session(self, user, session):
        self.users[user].session = session
        self.users[user].save()

    def set_user_full_name(self, user, first, last):
        self.users[user].first_name = first
        self.users[user].last_name = last
        self.users[user].save()


class SimpleBaseCase(BaseCase):
    test_admin = False
    test_rubric = False
    test_review = False
