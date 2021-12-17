from json import JSONDecoder, JSONEncoder
from uuid import uuid4

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


class RubricValidationTest(TestCase):

    def assertBad(self, error):
        form = RubricForm({'name': "Bad Rubric", 'rubric': JSONEncoder().encode(self.current)})
        if not form.is_valid():
            self.assertEqual(form.errors.get("rubric")[0], error + ".")
        else:
            self.fail("Invalid Rubric Passed Validation!")

    def setUp(self) -> None:
        self.current = JSONDecoder().decode(test_json)

    def test_bad_json(self):
        form = RubricForm({'name': "Bad Rubric", 'rubric': "Bad JSON!"})
        if not form.is_valid():
            self.assertEqual(form.errors.get("rubric")[0], "Invalid JSON")
        else:
            self.fail("Invalid Rubric Passed Validation!")

    def test_bad_structure(self):
        self.current = {'bad': "bad structure"}
        self.assertBad("Unknown Error")

    def test_bad_row_structure(self):
        self.current[0] = {'bad': "bad row structure"}
        self.assertBad("Unknown error in row 1")

    def test_bad_cell_structure(self):
        self.current[0]['cells'][0] = {'bad': "bad cell structure"}
        self.assertBad("Unknown error in row 1, cell 1")

    def test_no_rows(self):
        self.current = []
        self.assertBad("Please provide at least one row")

    def test_no_row_name(self):
        self.current[0]['name'] = ""
        self.assertBad("Please enter a name in row 1")

    def test_row_name_too_long(self):
        self.current[0]['name'] = "A" * 1000
        self.assertBad("name is too long in row 1")

    def test_row_description_too_long(self):
        self.current[0]['description'] = "A" * 1001
        self.assertBad("description is too long in row 1")

    def test_no_row_description(self):
        self.current[0]['description'] = ""
        self.assertBad("Please enter a description in row 1")

    def test_no_cells(self):
        self.current[0]['cells'] = []
        self.assertBad("Row 1 must have at least one cell")

    def test_no_cell_score(self):
        self.current[0]['cells'][0]['score'] = ""
        self.assertBad("Please enter a number for the score in row 1, cell 1")

    def test_cell_score_not_numeric(self):
        self.current[0]['cells'][0]['score'] = "as"
        self.assertBad("Please enter a number for the score in row 1, cell 1")

    def test_cell_score_negative(self):
        self.current[0]['cells'][0]['score'] = -5
        self.assertBad("The score must be between 0 and 100 in row 1, cell 1")

    def test_cell_score_big(self):
        self.current[0]['cells'][0]['score'] = 101
        self.assertBad("The score must be between 0 and 100 in row 1, cell 1")

    def test_no_cell_description(self):
        self.current[0]['cells'][0]['description'] = ""
        self.assertBad("Please enter a description in row 1, cell 1")

    def test_cell_description_too_long(self):
        self.current[0]['cells'][0]['description'] = "A" * 1001
        self.assertBad("Description is too long in row 1, cell 1")

    def test_good(self):
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


class RubricDuplicateTest(TestCase):

    def setUp(self) -> None:
        self.user = User.objects.create_superuser('admin')
        self.client.force_login(self.user)
        self.client.post(reverse('rubric-create'), {'name': "Source Rubric", "rubric": test_json})
        self.source_rubric = Rubric.objects.get(name='Source Rubric')

    def test_dupe(self) -> None:
        self.client.post(reverse('rubric-duplicate', kwargs={'pk': self.source_rubric.id}))
        new_rubric = Rubric.objects.get(name="Copy of Source Rubric")
        self.assertNotEqual(new_rubric.id, self.source_rubric.id)
        src_row = self.source_rubric.rubricrow_set.get(index=0)
        new_row = new_rubric.rubricrow_set.get(index=0)
        self.assertEqual(new_row.name, src_row.name)
        self.assertNotEqual(new_row.id, src_row.id)
        src_cell = src_row.rubriccell_set.get(index=0)
        new_cell = new_row.rubriccell_set.get(index=0)
        self.assertEqual(src_cell.score, new_cell.score)
        self.assertNotEqual(src_cell.id, new_cell.id)

    def test_invalid_id(self):
        self.source_rubric.delete()
        response = self.client.post(reverse('rubric-duplicate', kwargs={'pk': uuid4()}))
        self.assertEqual(response.templates[0].name, 'errors/404.html')


