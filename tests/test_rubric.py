from Main.models import Rubric, RubricRow, RubricCell

from django.test import TestCase
from Main.views import rubric_factory


class RubricFactory(TestCase):

    new_rubric = None
    rows = []

    def setUp(self) -> None:
        with open("tests/test_rubric.json", 'r') as file:
            test_json = file.read()
        self.new_rubric = rubric_factory(test_json)
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


