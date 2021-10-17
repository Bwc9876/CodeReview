from json import JSONDecoder, JSONEncoder

from django.test import TestCase, Client
from django.urls import reverse

from Instructor.models import Rubric, ScoredRow
from Main.forms import GradeReviewForm
from Main.models import Review
from Users.models import User

with open("tests/test_rubric.json", 'r') as file:
    test_json = file.read()


class BaseCase(TestCase):

    def create_user_matrix(self):
        users = {
            'reviewer-affiliated': User.objects.create_user("reviewer-affiliated", is_reviewer=True),
            'student-affiliated': User.objects.create_user("student-affiliated"),
            'reviewer-not': User.objects.create_user("reviewer-not", is_reviewer=True),
            'student-not': User.objects.create_user("student-not"),
            'super': User.objects.create_superuser("test-instructor"),
        }
        self.users = users

    def create_client_matrix(self):
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
                                            student=self.users['student-affiliated'],
                                            reviewer=self.users['reviewer-affiliated'])


class ReviewAccessTest(BaseCase):
    # noinspection SpellCheckingInspection
    expected = {
        'create': ("--yyy",),
        'edit': ("-ynnn", "-ynnn"),
        'cancel': ("nynnn", "nynnn", "nnnnn"),
        'delete': ("nnnny", "nnnny", "nnnny"),
        'claim': ("-nynn", "nnnnn", "nnnnn"),
        'abandon': ("nnnnn", "ynnnn", "nnnnn"),
        'grade': ("nnnnn", "ynnnn", "nnnnn"),
        'view': ("nnnnn", "nnnnn", "yynny")
    }

    def setUp(self) -> None:
        super().setUp()
        self.review.status = Review.Status.ASSIGNED
        self.review.save()
        self.clients['reviewer-affiliated'].post(reverse("review-grade", kwargs={'pk': self.review.id}),
                                                 {'scores': "[10,2]", 'additional_comments': ""})
        self.review.status = Review.Status.OPEN
        self.review.save()

    def assertResponses(self, expected_key, add_pk=True, http_type='get') -> None:
        target_statuses = self.expected[expected_key]
        if add_pk:
            url = reverse(f'review-{expected_key}', kwargs={'pk': self.review.id})
        else:
            url = reverse(f'review-{expected_key}')
        for index in range(len(target_statuses)):
            target_responses = target_statuses[index]
            self.review.status = Review.Status.values[index]
            self.review.save()
            for code_index, expected in enumerate(target_responses):
                if expected != "-":
                    client = self.clients.get(list(self.clients.keys())[code_index])
                    if http_type == 'get':
                        response = client.get(url)
                    else:
                        response = client.post(url)
                    if expected == "y":
                        self.assertIn(response.status_code, (200, 302))
                    elif expected == "n":
                        self.assertIn(response.status_code, (404, 403))
                    else:
                        self.fail("Invalid Setup Of Expected")

    def test_create(self) -> None:
        self.assertResponses('create', add_pk=False)

    def test_edit(self) -> None:
        self.assertResponses('edit')

    def test_cancel(self) -> None:
        self.assertResponses('cancel')

    def test_delete(self) -> None:
        self.assertResponses('delete')

    def test_claim(self) -> None:
        self.assertResponses('claim', http_type='post')

    def test_abandon(self) -> None:
        self.assertResponses('abandon')

    def test_grade(self) -> None:
        self.assertResponses('grade')

    def test_view(self) -> None:
        self.assertResponses('view')


class HomeListTest(BaseCase):
    expected = {
        "O": ("-", "active", "open", "none"),
        "A": ("assigned", "active", "none", "none"),
        "C": ("completed", "completed", "none", "none"),
    }

    url = reverse("home")

    def assertStatus(self, status_code):
        self.review.status = status_code
        self.review.save()
        for index, group in enumerate(self.expected[status_code]):
            if group != "-":
                response = self.clients.get(list(self.clients.keys())[index]).get(self.url)
                if group == "none":
                    for not_group in ["open", "assigned", "completed", "active"]:
                        self.assertNotIn(self.review, response.context.get(not_group, []))
                else:
                    self.assertIn(self.review, response.context.get(group, []))

    def test_open(self) -> None:
        self.assertStatus('O')

    def test_open_different_session(self) -> None:
        self.users['reviewer-not'].session = User.Session.PM
        self.users['reviewer-not'].save()
        response = self.clients['reviewer-not'].get(self.url)
        self.assertNotIn(self.review, response.context.get("open", []))

    def test_assigned(self) -> None:
        self.assertStatus('A')

    def test_closed(self) -> None:
        self.assertStatus('C')


class CompleteListTest(BaseCase):

    def setUp(self) -> None:
        super(CompleteListTest, self).setUp()
        self.review.status = Review.Status.ASSIGNED
        self.review.save()
        self.clients['reviewer-affiliated'].post(reverse('review-grade', kwargs={'pk': self.review.id}),
                                                 {'scores': "[10,2]"})

    def assertInContext(self, client, params=""):
        response = client.get(reverse('review-complete') + params)
        self.assertIn(self.review, response.context.get("reviews", []))

    def assertNotInContext(self, client, params=""):
        response = client.get(reverse('review-complete') + params)
        self.assertNotIn(self.review, response.context.get("reviews", []))

    def test_access(self):
        self.assertInContext(self.clients['student-affiliated'])
        self.assertInContext(self.clients['reviewer-affiliated'])
        self.assertNotInContext(self.clients['student-not'])
        self.assertNotInContext(self.clients['reviewer-not'])

    def test_pagination(self):
        response = self.clients['student-affiliated'].get(reverse('review-complete'))
        self.assertFalse(response.context['page_obj'].has_other_pages())
        for i in range(0, 12):
            new_review = Review.objects.create(rubric=self.rubric, schoology_id="12.34.56",
                                               student=self.users['student-affiliated'],
                                               reviewer=self.users['reviewer-affiliated'],
                                               status=Review.Status.ASSIGNED)
            self.clients['reviewer-affiliated'].post(reverse('review-grade', kwargs={'pk': new_review.id}),
                                                     {'scores': "[10,2]"})
        response = self.clients['student-affiliated'].get(reverse('review-complete'))
        self.assertTrue(response.context['page_obj'].has_other_pages())
        response = self.clients['student-affiliated'].get(reverse('review-complete') + "?page=2")
        self.assertEqual(response.status_code, 200)

    def test_instructor_view(self):
        self.assertInContext(self.clients['super'], params="?session=AM")
        self.assertNotInContext(self.clients['super'], params="?session=PM")


class BaseReviewAction(TestCase):
    url_name = ''
    start_reviewer = True
    start_review = True
    start_status = Review.Status.OPEN

    schoology_id = "12.34.56"

    def setUpUsers(self):
        self.reviewer = User.objects.create_user('reviewer', is_reviewer=True)
        self.student = User.objects.create_user('student')
        self.reviewer_client = Client()
        self.student_client = Client()
        self.reviewer_client.force_login(self.reviewer)
        self.student_client.force_login(self.student)
        self.super = User.objects.create_superuser('admin')
        self.super_client = Client()
        self.super_client.force_login(self.super)

    def setUpRubric(self):
        self.super_client.post(reverse('rubric-create'), {'name': "Test Rubric", 'rubric': test_json})
        self.rubric = Rubric.objects.get(name="Test Rubric")

    def setUp(self) -> None:
        self.setUpUsers()
        self.setUpRubric()
        if self.start_review:
            self.review = Review.objects.create(schoology_id=self.schoology_id, student=self.student,
                                                rubric=self.rubric)
            if self.start_reviewer:
                self.review.reviewer = self.reviewer
            self.review.status = self.start_status
            self.review.save()
            self.url = reverse(f'review-{self.url_name}', kwargs={'pk': self.review.id})
        else:
            self.url = reverse(f'review-{self.url_name}')


class ReviewCreateTest(BaseReviewAction):
    url_name = 'create'
    start_review = False
    start_reviewer = False

    def test_create(self) -> None:
        self.student_client.post(self.url, {'schoology_id': self.schoology_id, "rubric": str(self.rubric.id)})
        try:
            self.review = Review.objects.get(schoology_id=self.schoology_id)
        except Review.DoesNotExist:
            self.fail("Review Not Created Successfully")


class ReviewCancelUnclaimedTest(BaseReviewAction):
    url_name = 'cancel'
    start_review = True
    start_reviewer = False

    def test_cancel(self) -> None:
        self.student_client.post(self.url)
        self.assertTrue(Review.objects.filter(schoology_id=self.schoology_id).count() == 0)


class ReviewCancelClaimedTest(ReviewCancelUnclaimedTest):
    start_reviewer = True
    start_status = Review.Status.ASSIGNED


class ReviewEditUnclaimedTest(BaseReviewAction):
    url_name = 'edit'
    start_review = True
    start_reviewer = False

    def test_edit(self) -> None:
        self.student_client.post(self.url, {'schoology_id': "12.34.78", "rubric": self.rubric.id})
        self.assertTrue(Review.objects.filter(schoology_id="12.34.78").count() > 0)


class ReviewEditClaimedTest(ReviewEditUnclaimedTest):
    start_reviewer = True
    start_status = Review.Status.ASSIGNED


class ReviewClaimTest(BaseReviewAction):
    url_name = 'claim'
    start_review = True
    start_reviewer = False

    def test_claim(self) -> None:
        self.reviewer_client.post(self.url)
        new_review = Review.objects.get(schoology_id=self.schoology_id)
        self.assertEqual(Review.Status.ASSIGNED, new_review.status)
        self.assertEqual(self.reviewer, new_review.reviewer)

    def test_claim_different_session(self) -> None:
        self.reviewer.session = User.Session.PM
        self.reviewer.save()
        response = self.reviewer_client.post(self.url)
        self.assertEqual(response.status_code, 404)


class ReviewAbandonTest(BaseReviewAction):
    url_name = 'abandon'
    start_review = True
    start_reviewer = True
    start_status = Review.Status.ASSIGNED

    def test_abandon(self) -> None:
        self.reviewer_client.post(self.url)
        new_review = Review.objects.get(schoology_id=self.schoology_id)
        self.assertEqual(Review.Status.OPEN, new_review.status)
        self.assertIsNone(new_review.reviewer)


class ReviewGradeTest(BaseReviewAction):
    url_name = 'grade'
    start_review = True
    start_reviewer = True
    start_status = Review.Status.ASSIGNED

    def assertScoresEqual(self, source_str, target_str):
        self.reviewer_client.post(self.url, {'scores': source_str, "additional_comments": ""})
        new_review = Review.objects.get(schoology_id=self.schoology_id)
        self.assertEqual(new_review.score_fraction(), target_str)

    def assertBad(self, src_str):
        form = GradeReviewForm({'scores': src_str, "additional_comments": ""}, instance=self.review)
        self.assertFalse(form.is_valid())

    def test_grade(self) -> None:
        self.assertScoresEqual("[5,2]", "7.0/12.0")

    def test_grade_with_na(self) -> None:
        self.assertScoresEqual("[5,-1]", "5.0/10.0")

    def test_grade_not_json(self) -> None:
        self.assertBad("not json")

    def test_grade_non_numeric(self) -> None:
        self.assertBad("[not,numeric]")

    def test_grade_none(self) -> None:
        self.assertBad("[]")

    def test_grade_too_much(self) -> None:
        self.assertBad("[1,1,1,1,1,1]")

    def test_grade_under_limit(self) -> None:
        self.assertBad("[-50,2]")


class UpdateReviewScoreOnRubricEditTest(BaseCase):

    def setUp(self) -> None:
        super(UpdateReviewScoreOnRubricEditTest, self).setUp()
        self.review.status = Review.Status.ASSIGNED
        self.review.save()
        self.clients['reviewer-affiliated'].post(reverse('review-grade', kwargs={'pk': self.review.id}),
                                                 {'scores': "[10,2]"})

    def test_new_rows(self) -> None:
        new_obj = JSONDecoder().decode(test_json)
        new_obj.append({
            'name': "New Row",
            'description': "New Row 3",
            'cells': [
                {
                    'score': 1,
                    'description': "New Cell 1"
                },
                {
                    'score': 0,
                    'description': "New Cell 2"
                }
            ]
        })
        self.clients['super'].post(reverse('rubric-edit', kwargs={'pk': self.rubric.id}),
                                   {'name': "Edited Rubric", 'rubric': JSONEncoder().encode(new_obj)})
        self.assertEqual(ScoredRow.objects.filter(parent_review__id=self.review.id).count(), 3)
        self.assertEqual(ScoredRow.objects.get(parent_review=self.review, source_row__index=2).score, -1)

    def test_delete_row(self):
        new_obj: list = JSONDecoder().decode(test_json)
        new_obj.pop(1)
        self.clients['super'].post(reverse('rubric-edit', kwargs={'pk': self.rubric.id}),
                                   {'name': "Edited Rubric", 'rubric': JSONEncoder().encode(new_obj)})
        self.assertEqual(ScoredRow.objects.filter(parent_review__id=self.review.id).count(), 1)
