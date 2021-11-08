from json import JSONEncoder

from django.test import TestCase, Client
from django.urls import reverse

from Instructor.models import Rubric
from Main.models import Review
from Users.models import User

with open("tests/test_rubric.json", 'r') as file:
    test_json = file.read()


class ListPageAccessTest(TestCase):

    def setUp(self) -> None:
        self.bad = User.objects.create_user(username="test-user")
        self.super = User.objects.create_superuser(username="test-instructor")
        self.bad_client = Client()
        self.bad_client.force_login(self.bad)
        self.super_client = Client()
        self.super_client.force_login(self.super)

    urls = ['instructor-home', 'user-list', 'rubric-list']

    def test_access(self):
        for url in self.urls:
            response = self.bad_client.get(reverse(url))
            self.assertEqual('errors/403.html', response.template_name[0])
            response = self.super_client.get(reverse(url))
            self.assertEqual(response.status_code, 200)


class HomeViewTest(TestCase):

    def create_user_matrix(self) -> None:
        users = {
            'reviewer': User.objects.create_user("reviewer-affiliated", is_reviewer=True),
            'student': User.objects.create_user("student-affiliated"),
            'super': User.objects.create_superuser("test-instructor"),
        }
        self.users = users

    def create_client_matrix(self) -> None:
        clients = {}
        for key in self.users.keys():
            val = self.users.get(key)
            new_client = Client()
            new_client.force_login(val)
            clients[key] = new_client
        self.clients = clients

    def setUp(self) -> None:
        self.create_user_matrix()
        self.create_client_matrix()
        self.clients['super'].post(reverse("rubric-create"), {'name': "Test Review Rubric", 'rubric': test_json})
        self.rubric = Rubric.objects.get(name="Test Review Rubric")
        self.review = Review.objects.create(rubric=self.rubric, schoology_id="03.04.05",
                                            student=self.users['student'],
                                            reviewer=self.users['reviewer'])

    def test_ongoing(self) -> None:
        self.review.status = Review.Status.ASSIGNED
        self.review.save()
        response = self.clients['super'].get(reverse('instructor-home'))
        self.assertIn(self.review, response.context.get('am_active', []))

    def test_ongoing_pm(self) -> None:
        self.users['student'].session = User.Session.PM
        self.users['student'].save()
        self.review.status = Review.Status.ASSIGNED
        self.review.save()
        response = self.clients['super'].get(reverse('instructor-home'))
        self.assertIn(self.review, response.context.get('pm_active', []))

    def test_completed(self) -> None:
        self.review.status = Review.Status.ASSIGNED
        self.review.save()
        self.clients['reviewer'].post(reverse('review-grade', kwargs={'pk': self.review.id}), {'scores': "[10,2]"})
        response = self.clients['super'].get(reverse('instructor-home'))
        self.assertIn(self.review, response.context.get('am_completed', []))

    def test_completed_pm(self) -> None:
        self.users['student'].session = User.Session.PM
        self.users['student'].save()
        self.review.status = Review.Status.ASSIGNED
        self.review.save()
        self.clients['reviewer'].post(reverse('review-grade', kwargs={'pk': self.review.id}), {'scores': "[10,2]"})
        response = self.clients['super'].get(reverse('instructor-home'))
        self.assertIn(self.review, response.context.get('pm_completed', []))


class UserDesignationTest(TestCase):
    url = reverse('user-list')

    def create_user_matrix(self) -> None:
        users = {
            'reviewer-am': User.objects.create_user("reviewer-am", is_reviewer=True),
            'student-am': User.objects.create_user("student-am"),
            'reviewer-pm': User.objects.create_user("reviewer-pm", is_reviewer=True, session=User.Session.PM),
            'student-pm': User.objects.create_user("student-pm", session=User.Session.PM),
            'super': User.objects.create_superuser("test-instructor"),
        }
        self.users = users

    def create_client_matrix(self) -> None:
        clients = {}
        for key in self.users.keys():
            val = self.users.get(key)
            new_client = Client()
            new_client.force_login(val)
            clients[key] = new_client
        self.clients = clients

    def setUp(self) -> None:
        self.create_user_matrix()
        self.create_client_matrix()

    def make_reviewers_list(self, user_list):
        ids = [str(self.users[user].id) for user in user_list]
        return ids

    def test_designate_reviewer(self) -> None:
        self.clients['super'].post(reverse('user-list'), data={
            'reviewers': self.make_reviewers_list(['reviewer-am', 'student-am']),
        })
        self.assertTrue(User.objects.get(username="reviewer-am").is_reviewer)
        self.assertFalse(User.objects.get(username="reviewer-pm").is_reviewer)
        self.assertTrue(User.objects.get(username="student-am").is_reviewer)
        self.assertFalse(User.objects.get(username="student-pm").is_reviewer)
