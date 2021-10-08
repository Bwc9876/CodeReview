let table = undefined;
let scoreHeader = undefined;

function convert_from_json(src_json) {

    if (src_json === "{}") return;

    let src_obj = JSON.parse(src_json);

    for (let i = 0; i < src_obj.rows.length; i++) {

        let row = src_obj.rows[i];
        let row_elem = $(table.find(".row").eq(i));
        row_elem.find(".row-name").val(row['name']);
        row_elem.find(".row-description").val(row['description']);

        for (let y = 0; y < row.cells.length; y++) {

            let cell = row.cells[y];
            let cell_elem = $(row_elem.children(".data-cell").eq(y));
            cell_elem.find(".cell-score").val(cell['score']);
            cell_elem.find(".cell-description").val(cell['description']);

            if (y !== row.cells.length - 1) row_elem.find(".add-cell-button").click();

        }

        if (i !== src_obj.rows.length - 1) $(".add-row-button").click();

    }

}

function convert_to_json() {

    let new_rubric = {"rows": []};

    table.find(".row").each(function (index, object) {

        let new_row = {
            "name": $(object).find(".row-name").val(),
            "description": $(object).find(".row-description").val(),
            "cells": []
        };

        $(object).children(".data-cell").each(function (index, cell) {

            let new_cell = {
                "score": $(cell).find(".cell-score").val(),
                "description": $(cell).find(".cell-description").val()
            };
            new_row["cells"].push(new_cell);

        });

        new_rubric["rows"].push(new_row);

    });

    return JSON.stringify(new_rubric);

}

function delete_row_callback(event) {

    $(event.target).parents("tr").remove();

}

function delete_cell_callback(event) {

    $(event.target).parents("td").remove();

}

function add_row_callback() {
    let new_row = $("<tr>");
    new_row.addClass("row");
    new_row.html(`<th class="cell">
                        <div class="cell-wrapper">
                            <button type="button" class="delete-button delete-row">X</button>
                            <div class="cell_part">
                                <label>
                                    Name: <input class="cell-input row-name" type="text"/>
                                </label>
                            </div>
                            <div class="cell_part">
                                <label>
                                    Description: <input class="cell-input row-description" type="text"/>
                                </label>
                            </div>
                        </div>
                    </th>
                    <td class="cell data-cell">
                        <div class="cell-wrapper">
                            <button type="button" class="delete-button delete-cell">X</button>
                            <div class="cell_part">
                                <label>
                                    Score: <input class="cell-input cell-score" type="number"/>
                                </label>
                            </div>
                            <div class="cell_part">
                                <label>
                                    Description: <input class="cell-input cell-description" type="text"/>
                                </label>
                            </div>
                        </div>
                    </td>
                    <td class="cell">
                        <button type="button" class="add-cell-button">Add Cell</button>
                    </td>`);
    table.append(new_row);
    new_row.find(".add-cell-button").click(add_cell_callback);
    new_row.find(".delete-row").click(delete_row_callback);
    new_row.find(".delete-cell").click(delete_cell_callback);
}

function add_cell_callback(event) {
    let new_cell = $("<td>");
    new_cell.addClass("cell");
    new_cell.addClass("data-cell");
    new_cell.html(`
            <div class="cell-wrapper">
                <button type="button" class="delete-button delete-cell">X</button>
                <div class="cell_part">
                    <label>
                        Score: <input class="cell-input cell-score" type="number"/>
                    </label>
                </div>
                <div class="cell_part">
                    <label>
                        Description: <input class="cell-input cell-description" type="text"/>
                    </label>
                </div>
            </div>
        `);
    $(event.target).parent().before(new_cell);
    new_cell.find(".delete-cell").click(delete_cell_callback);
    let new_cell_count = $(event.target).parents("tr").children().length;
    if (new_cell_count > scoreHeader.attr('colspan')) scoreHeader.attr('colspan', new_cell_count);
}


function submit_callback() {

    $(".rubric_create_input").val(convert_to_json());

}


$(document).ready(() => {

    table = $(".rubric-edit-table");
    scoreHeader = $("#scoreHeader");

    $(".add-row-button").click(add_row_callback);
    $(".add-cell-button").click(add_cell_callback);
    $(".delete-row").click(delete_row_callback);
    $(".delete-cell").click(delete_cell_callback);

    $(".form").submit(submit_callback);

    convert_from_json($(".rubric_create_input").val())

});