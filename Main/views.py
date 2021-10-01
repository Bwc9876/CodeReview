from typing import Union

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render, get_object_or_404

from . import models, forms


def home_view(request) -> HttpResponse:
    return render(request, "home.html")


def edit_rubric(request) -> Union[HttpResponse, HttpResponseRedirect]:
    current_id: str = request.GET.get("id", "")
    if request.method == "GET":
        if current_id == "":
            form = forms.RubricForm()
        else:
            current_rubric = get_object_or_404(models.Rubric, id=models.val_uuid(current_id))
            form = forms.RubricForm({'name': current_rubric.name, 'rubric': current_rubric.to_json()})
        return render(request, 'form_base.html', {'form': form})
    elif request.method == "POST":
        form = forms.RubricForm(request.POST)
        if form.is_valid():
            current_id: str = request.GET.get("id", None)
            data = form.cleaned_data
            models.Rubric.create_from_json(data.get("name"), data.get("rubric"), current_id=models.val_uuid(current_id))
            return redirect("home")
        else:
            return render(request, 'form_base.html', {'form': form})
