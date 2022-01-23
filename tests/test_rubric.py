from json import JSONDecoder, JSONEncoder
from uuid import uuid4

from django.test import TestCase
from django.urls import reverse

from Instructor.forms import RubricForm
from Instructor.models import Rubric
from tests.testing_base import SimpleBaseCase


class RubricFormTest(SimpleBaseCase):
    test_admin = True
    test_users = SimpleBaseCase.USER_SINGLE_STUDENT

    new_rubric = None
    rows = []

    def test_access(self):
        bad_response = self.get('test-user', reverse('rubric-create'))
        self.assertEqual(bad_response.template_name[0], 'errors/403.html')
        good_response = self.get('super', reverse('rubric-create'))
        self.assertEqual(good_response.status_code, 200)

    def test_form(self):
        self.post('super', reverse('rubric-create'), {'name': 'Create Rubric', 'rubric': self.get_test_rubric_json()})
        try:
            new_rubric = Rubric.objects.get(name='Create Rubric')
            self.assertEqual(new_rubric.max_score, 12)
            d = JSONDecoder()
            self.assertListEqual(d.decode(self.get_test_rubric_json()), d.decode(new_rubric.to_json()))
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
        self.current = JSONDecoder().decode(SimpleBaseCase.get_test_rubric_json())

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
        form = RubricForm({'name': "Good Rubric", 'rubric': SimpleBaseCase.get_test_rubric_json()})
        self.assertTrue(form.is_valid())


class RubricActionTest(SimpleBaseCase):
    url_name = ""
    test_admin = True
    test_rubric = True

    def setUp(self) -> None:
        super(RubricActionTest, self).setUp()
        self.url = reverse(self.url_name, kwargs={'pk': self.rubric.id})


class RubricDeleteTest(RubricActionTest):
    url_name = "rubric-delete"

    # noinspection PyTypeChecker
    def test_delete(self):
        self.post('super', self.url)
        self.assertFalse(Rubric.objects.filter(id=self.rubric.id).exists())

    def test_get(self):
        response = self.get('super', self.url)
        self.assertEqual(200, response.status_code)


class RubricEditTest(RubricActionTest):
    url_name = "rubric-edit"

    def test_edit(self):
        new_json = JSONDecoder().decode(self.get_test_rubric_json())
        new_json[0]['description'] = "New desc"
        new_json[1]['name'] = "New Row"
        new_json[0]['cells'][0]['score'] = 30
        new_json[1]['cells'][1]['description'] = "New desc"
        self.post('super', self.url, {"name": self.rubric.name + " Edited", "rubric": JSONEncoder().encode(new_json)})
        new_rubric = Rubric.objects.get(name=self.rubric.name + " Edited")
        self.assertListEqual(JSONDecoder().decode(new_rubric.to_json()), new_json)
        self.assertEqual(new_rubric.max_score, 32)
        self.assertEqual(new_rubric.rubricrow_set.get(index=0).max_score, 30)


class RubricListTest(SimpleBaseCase):
    test_admin = True
    test_users = SimpleBaseCase.USER_SINGLE_STUDENT
    test_rubric = True

    def test_access(self):
        self.assertEqual('errors/403.html', self.get('test-user', reverse('rubric-list')).template_name[0])
        self.assertEqual(200, self.get('super', reverse('rubric-list')).status_code)

    def test_list(self):
        response = self.get('super', reverse('rubric-list'))
        self.assertIn(self.rubric, response.context['rubrics'])


class RubricDuplicateTest(SimpleBaseCase):
    test_admin = True
    test_rubric = True

    def test_dupe(self) -> None:
        self.post('super', reverse('rubric-duplicate', kwargs={'pk': self.rubric.id}))
        new_rubric = Rubric.objects.get(name="Copy of Test Rubric")
        self.assertNotEqual(new_rubric.id, self.rubric.id)
        src_row = self.rubric.rubricrow_set.get(index=0)
        new_row = new_rubric.rubricrow_set.get(index=0)
        self.assertEqual(new_row.name, src_row.name)
        self.assertNotEqual(new_row.id, src_row.id)
        src_cell = src_row.rubriccell_set.get(index=0)
        new_cell = new_row.rubriccell_set.get(index=0)
        self.assertEqual(src_cell.score, new_cell.score)
        self.assertNotEqual(src_cell.id, new_cell.id)

    def test_invalid_id(self):
        self.rubric.delete()
        response = self.post('super', reverse('rubric-duplicate', kwargs={'pk': uuid4()}))
        self.assertEqual(response.templates[0].name, 'errors/404.html')

    def test_name_long(self):
        self.rubric.name = "A" * 49
        self.rubric.save()
        self.post('super', reverse('rubric-duplicate', kwargs={'pk': self.rubric.id}))
        self.assertTrue(Rubric.objects.filter(name="New Rubric").exists())
