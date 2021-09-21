from django import template
from django.template.loader import render_to_string

from Main.models import RubricRow, RubricCell

register = template.Library()


@register.filter(name="rubric_render")
def render(rubric):
    rubric_rows = RubricRow.objects.filter(parent_rubric=rubric)
    rubric_cells = [RubricCell.objects.filter(parent_row=row) for row in rubric_rows]

    rubric_data = []

    for x in range(rubric_rows):
        rubric_data.append((rubric_rows[x], rubric_cells[x]))

    return render_to_string("""
    <table class="rubric">
            <tr class="rubric-headers">
                <th>Category</th>
                <th colspan="{{ rows|length }}">Score</th>
            </tr>
            {% for row in rubric_data %}
                <tr class="rubric-row">
                    <th class="rubric-cell row-header"><b>{{ row.0.name }}</b> &nbsp; {{ row.0.description }}</th>
                    {% for cell in row.1 %}
                        <td class="rubric-cell"><b>{{ cell.score }}</b> &nbsp; {{ cell.description }}</td>
                    {% endfor %}
                </tr>
            {% endfor %}
    </table>
    """, {'rubric': rubric, "rubric_data": rubric_data})
