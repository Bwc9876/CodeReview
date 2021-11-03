from json import JSONDecoder, JSONEncoder

from django.test import TestCase, Client
from django.urls import reverse

from Instructor.forms import RubricForm
from Instructor.models import Rubric
from Users.models import User

with open("tests/test_rubric.json", 'r') as file:
    test_json = file.read()


class RubricFormTest(TestCase):
    new_rubric = None
    rows = []

    def setUp(self):
        self.user = User.objects.create_user('test-user')
        self.user.is_superuser = True
        self.user.save()
        self.client = Client()
        self.client.force_login(self.user)
        self.url = reverse('rubric-create')

    def test_access(self):
        bad_user = User.objects.create_user('unauthorized_user_for_rubrics')
        bad_user.save()
        c = Client()
        c.force_login(bad_user)
        bad_response = c.get(self.url)
        self.assertEqual(bad_response.template_name[0], 'errors/403.html')
        good_response = self.client.get(self.url)
        self.assertNotEqual(good_response.template_name[0], 'errors/403.html')

    def test_form(self):
        post_data = {'name': 'Create Rubric', 'rubric': test_json}
        self.client.post(self.url, post_data)
        try:
            new_rubric = Rubric.objects.get(name='Create Rubric')
            self.assertEqual(new_rubric.max_score, 12)
            d = JSONDecoder()
            self.assertListEqual(d.decode(test_json), d.decode(new_rubric.to_json()))
            self.assertEquals(10, new_rubric.rubricrow_set.get(index=0).max_score)
            self.assertEquals(2, new_rubric.rubricrow_set.get(index=1).max_score)
        except Rubric.DoesNotExist:
            self.fail("Rubric Not Created")

    def assertBad(self, src_dict, error):
        form = RubricForm({'name': "Bad Rubric", 'rubric': JSONEncoder().encode(src_dict)})
        if not form.is_valid():
            self.assertEqual(form.errors.get("rubric")[0], error + ".")
        else:
            self.fail("Invalid Rubric Passed Validation!")

    def new_current(self) -> list:
        return JSONDecoder().decode(test_json)

    def test_validation(self):
        current = []
        self.assertBad(current, "Please provide at least one row")
        current = self.new_current()
        current[0]['name'] = ""
        self.assertBad(current, "Please enter a name in row 1")
        current = self.new_current()
        current[0]['description'] = ""
        self.assertBad(current, "Please enter a description in row 1")
        current = self.new_current()
        current[0]['cells'] = []
        self.assertBad(current, "Row 1 must have at least one cell")
        current = self.new_current()
        current[0]['cells'][0]['score'] = ""
        self.assertBad(current, "Please enter a number for the score in row 1, cell 1")
        current = self.new_current()
        current[0]['cells'][0]['description'] = ""
        self.assertBad(current, "Please enter a description in row 1, cell 1")

        form = RubricForm({'name': "Good Rubric", 'rubric': test_json})
        self.assertTrue(form.is_valid())


class RubricActionTest(TestCase):
    rubric_name = ""
    url_name = ""

    def setUp(self):
        self.user = User.objects.create_superuser(username="test-user")
        self.client = Client()
        self.client.force_login(self.user)
        self.client.post(reverse('rubric-create'), {'name': self.rubric_name, "rubric": test_json})
        self.rubric = Rubric.objects.get(name=self.rubric_name)
        self.url = reverse(self.url_name, kwargs={'pk': self.rubric.id})


class RubricDeleteTest(RubricActionTest):
    rubric_name = "Deleted Rubric"
    url_name = "rubric-delete"

    def test_access(self):
        bad_user = User.objects.create_user("bad-user")
        bad_client = Client()
        bad_client.force_login(bad_user)
        self.assertEqual('errors/403.html', bad_client.get(self.url).template_name[0])
        self.assertNotEqual('errors/403.html', self.client.get(self.url).template_name[0])

    # noinspection PyTypeChecker
    def test_delete(self):
        self.client.post(self.url)

        def get_rubric():
            Rubric.objects.get(name=self.rubric_name)

        self.assertRaises(Rubric.DoesNotExist, get_rubric)


class RubricEditTest(RubricActionTest):
    rubric_name = "Edited Rubric"
    url_name = "rubric-edit"

    def test_access(self):
        bad_user = User.objects.create_user("bad-user")
        bad_client = Client()
        bad_client.force_login(bad_user)
        self.assertEqual('errors/403.html', bad_client.get(self.url).template_name[0])
        self.assertNotEqual('errors/403.html', self.client.get(self.url).template_name[0])

    def test_edit(self):
        new_json = JSONDecoder().decode(test_json)
        new_json[0]['description'] = "New desc"
        new_json[1]['name'] = "New Row"
        new_json[0]['cells'][0]['score'] = 30
        new_json[1]['cells'][1]['description'] = "New desc"
        self.client.post(self.url, {"name": self.rubric_name, "rubric": JSONEncoder().encode(new_json)})
        new_rubric = Rubric.objects.get(name=self.rubric_name)
        self.assertListEqual(JSONDecoder().decode(new_rubric.to_json()), new_json)
        self.assertEqual(new_rubric.max_score, 32)
        self.assertEqual(new_rubric.rubricrow_set.get(index=0).max_score, 30)


class RubricListTest(TestCase):

    def setUp(self) -> None:
        self.user = User.objects.create_superuser(username="test-user")
        self.client = Client()
        self.client.force_login(self.user)
        self.client.post(reverse('rubric-create'), {'name': "Listed Rubric", "rubric": test_json})
        self.rubric = Rubric.objects.get(name="Listed Rubric")
        self.url = reverse('rubric-list')

    def test_access(self):
        bad_user = User.objects.create_user("bad-user")
        bad_client = Client()
        bad_client.force_login(bad_user)
        self.assertEqual('errors/403.html', bad_client.get(self.url).template_name[0])
        self.assertNotEqual('errors/403.html', self.client.get(self.url).template_name[0])

    def test_list(self):
        response = self.client.get(self.url)
        self.assertIn(self.rubric, response.context['rubrics'])
