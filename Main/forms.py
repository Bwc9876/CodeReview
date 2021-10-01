from json import JSONDecoder, JSONDecodeError

from django.forms import Form, ModelForm, Field, TextInput
from django.forms.fields import CharField

from . import models


class CreateRubricWidget(TextInput):
    template_name = "widgets/create_rubric.html"

    class Media:
        css = {'all': ('css/rubric_create.css',)}
        js = ('js/rubric-create-widget.js',)


class CreateRubricField(Field):
    widget = CreateRubricWidget()


class RubricForm(Form):
    name = CharField(max_length=100)
    rubric = CreateRubricField()

    def json_exit(self) -> None:
        self.add_error('rubric', "Invalid JSON")

    def clean(self) -> None:
        cleaned_data: dict = super().clean()
        raw_json: str = cleaned_data.get("rubric")

        if raw_json is not None:
            try:
                obj: dict = dict(JSONDecoder().decode(cleaned_data.get("rubric")))
                if "rows" in obj.keys():
                    rows = obj.get("rows")
                    if type(rows) == list:
                        for row in rows:
                            if type(row) == dict:
                                if "name" not in row.keys():
                                    self.json_exit()
                                    return
                                if "description" not in row.keys():
                                    self.json_exit()
                                    return
                                if "cells" in row.keys():
                                    cells = row.get("cells")
                                    if type(cells) == list:
                                        for cell in cells:
                                            if type(cell) == dict:
                                                if "description" not in cell.keys():
                                                    self.json_exit()
                                                    return
                                                if "score" in cell.keys():
                                                    try:
                                                        int(cell.get("score"))
                                                    except ValueError:
                                                        self.json_exit()
                                                        return
                                                else:
                                                    self.json_exit()
                                                    return
                                            else:
                                                self.json_exit()
                                                return
                                    else:
                                        self.json_exit()
                                        return
                                else:
                                    self.json_exit()
                                    return
                            else:
                                self.json_exit()
                                return
                    else:
                        self.json_exit()
                        return
                else:
                    self.json_exit()
                    return
            except JSONDecodeError:
                self.json_exit()


class CreateReviewForm(ModelForm):
    class Meta:
        model = models.Review
        fields = ['schoology_id', 'rubric']
