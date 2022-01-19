from uuid import uuid4

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

    def test_redirect(self) -> None:
        self.clients['super'].post(reverse('user-setup', kwargs={'pk': self.users['super'].id}), {'email': "admin"})
        response = self.clients['super'].get(reverse('home'))
        self.assertRedirects(response, reverse('instructor-home'))

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

    def test_completed_overflow(self) -> None:
        for x in range(5):
            new_review = Review.objects.create(student=self.users['student'], schoology_id=f"12.34.0{x}",
                                               reviewer=self.users['reviewer'], status=Review.Status.ASSIGNED,
                                               rubric=self.rubric)
            self.clients['reviewer'].post(reverse('review-grade', kwargs={'pk': new_review.id}), {'scores': "[10,2]"})
        response = self.clients['super'].get(reverse('instructor-home'))
        self.assertIn("review/completed/?session=AM", str(response.content))

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

    def test_delete_users(self) -> None:
        self.clients['super'].post(reverse('user-list'), data={
            'to_delete': self.make_reviewers_list(['reviewer-am', 'student-am']),
        })
        self.assertFalse(User.objects.filter(username="reviewer-am"))
        self.assertFalse(User.objects.filter(username="student-am"))

    def test_delete_pm(self) -> None:
        self.clients['super'].post(reverse('user-list'), data={
            'to_delete': self.make_reviewers_list(['reviewer-pm', 'student-am']),
        })
        self.assertFalse(User.objects.filter(username="reviewer-pm"))
        self.assertFalse(User.objects.filter(username="student-am"))

    def test_no_reviewers(self) -> None:
        self.clients['super'].post(reverse('user-list'), data={
            'reviewers': [],
        })
        self.assertFalse(User.objects.get(username="reviewer-am").is_reviewer)
        self.assertFalse(User.objects.get(username="reviewer-pm").is_reviewer)
        self.assertFalse(User.objects.get(username="student-am").is_reviewer)
        self.assertFalse(User.objects.get(username="student-pm").is_reviewer)

    def test_user_doesnt_exist(self) -> None:
        self.clients['super'].post(reverse('user-list'), data={
            'reviewers': self.make_reviewers_list(['reviewer-am']) + [uuid4()], 'to_delete': self.make_reviewers_list(['student-am']) + [uuid4()]
        })
        self.assertTrue(User.objects.get(username="reviewer-am").is_reviewer)
        self.assertFalse(User.objects.filter(username="student-am").exists())

    def test_reviewers_invalid_uuid(self) -> None:
        response = self.clients['super'].post(reverse('user-list'), data={
            'reviewers': ["bad-uuid"], 'to_delete': []
        })
        self.assertIn("Invalid User IDs", [m.message for m in get_messages(response.wsgi_request)])

    def test_delete_invalid_uuid(self) -> None:
        response = self.clients['super'].post(reverse('user-list'), data={
            'reviewers': self.make_reviewers_list(["reviewer-am", "reviewer-pm"]), 'to_delete': ["bad-uuid"]
        })
        self.assertIn("Invalid User IDs", [m.message for m in get_messages(response.wsgi_request)])
