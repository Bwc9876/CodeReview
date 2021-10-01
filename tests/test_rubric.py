from Main.models import Rubric, RubricRow, RubricCell
from Main.forms import RubricForm

from django.test import TestCase


class RubricValidation(TestCase):

    def assertBad(self, json):
        form = RubricForm({'name': "Bad Rubric", 'rubric': json})
        self.assertFalse(form.is_valid())

    def test_bad_json(self):
        self.assertBad("Im bad json!")

    def test_no_rows(self):
        self.assertBad('{"som-other-val": "Im some other val!"}')

    def test_rows_string(self):
        self.assertBad('{"rows": "Uh oh"}')

    def test_rows_are_not_dicts(self):
        self.assertBad('{"rows": [3, 4, 5]}')

    def test_rows_no_name(self):
        self.assertBad('{"rows": [{"description": "a", "cells": []}]}')

    def test_rows_no_desc(self):
        self.assertBad('{"rows": [{"name": "a", "cells": []}]}')

    def test_rows_no_cells(self):
        self.assertBad('{"rows": [{"name": "a", "description": "a"}]}')

    def test_row_cell_is_not_list(self):
        self.assertBad('{"rows": [{"name": "a", "description": "a", "cells": "uh oh"}]}')

    def test_row_cell_is_not_dict(self):
        self.assertBad('{"rows": [{"name": "a", "description": "a", "cells": [3, 4, 5]}]}')

    def test_row_cell_no_desc(self):
        self.assertBad('{"rows": [{"name": "a", "description": "a", "cells": [{"score": 5}]}]}')

    def test_row_cell_no_score(self):
        self.assertBad('{"rows": [{"name": "a", "description": "a", "cells": [{"description": "a"}]}]}')

    def test_row_cell_score_non_numeric(self):
        self.assertBad('{"rows": [{"name": "a", "description": "a", "cells": [{"description": "a", "score": "aaa"}]}]}')

    def test_good_rubric(self):
        self.assertTrue(RubricForm(
            {'name': "Good Rubric",
             'rubric':
                 '{"rows": '
                 '[{"name": "cool row", "description": "cool row!!!", "cells":[{"score":5, "description": "is cool"}]}]'
                 '}'
             }).is_valid())


class RubricFactory(TestCase):
    new_rubric = None
    rows = []

    def setUp(self):
        with open("tests/test_rubric.json", 'r') as file:
            test_json = file.read()
        self.new_rubric = Rubric.create_from_json("Test Rubric", test_json)
        self.rows = RubricRow.objects.filter(parent_rubric=self.new_rubric)

    def test_rubric_main(self):
        self.assertEquals(self.new_rubric.name, "Test Rubric")
        self.assertEquals(self.new_rubric.max_score, 12)

    def test_rubric_rows(self):
        row_1 = self.rows[0]
        self.assertEquals(row_1.name, "row 1")
        self.assertEquals(row_1.description, "row desc 1")
        self.assertEquals(row_1.max_score, 10)
        row_2 = self.rows[1]
        self.assertEquals(row_2.name, "row 2")
        self.assertEquals(row_2.description, "row desc 2")
        self.assertEquals(row_2.max_score, 2)

    def test_rubric_cells(self):
        row_1_cells = RubricCell.objects.filter(parent_row=self.rows[0])
        row_1_cell_1 = row_1_cells[0]
        row_1_cell_2 = row_1_cells[1]
        self.assertEquals(row_1_cell_1.description, "cell 2 row 1")
        self.assertEquals(row_1_cell_2.description, "cell 1 row 1")
        self.assertEquals(row_1_cell_1.score, 10)
        self.assertEquals(row_1_cell_2.score, 5)

        row_2_cells = RubricCell.objects.filter(parent_row=self.rows[1])
        row_2_cell_1 = row_2_cells[0]
        row_2_cell_2 = row_2_cells[1]
        self.assertEquals(row_2_cell_1.description, "cell 1 row 2")
        self.assertEquals(row_2_cell_2.description, "cell 2 row 2")
        self.assertEquals(row_2_cell_1.score, 2)
        self.assertEquals(row_2_cell_2.score, 1)
