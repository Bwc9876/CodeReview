let table = undefined;
let scoreHeader = undefined;
let current_row = 2;
let cell_counts = [2];
let max_cells = 2;

function convert_from_json(src_json) {

    let src_obj = JSON.parse(src_json);

}

function convert_to_json() {

    let new_rubric = {"name": "temp", "rows": []};

    $(".rubric-edit-table .row").each(function(index, object) {

        let new_row = {"name": $(`#${object.id}-name`).val(), "description": $(`#${object.id}-description`).val(), "cells": []};

        $(`#${object.id} .data-cell`).each(function(index, cell) {

            let new_cell = {"score": parseInt($(`#${cell.id}-score`).val()), "description": $(`#${cell.id}-description`).val()};
            new_row["cells"].push(new_cell);

        });

        new_rubric["rows"].push(new_row);

    });

    return JSON.stringify(new_rubric);

}

function add_row_callback(event) {

    let new_row = $("<tr>");
    new_row.attr('id', `row-${current_row}`);
    new_row.addClass("row");
    new_row.html(`<th class="cell">
                        <div class="cell-wrapper">
                            <p>Row ${current_row}</p>
                            <div class="cell_part">
                                <label for="row-${current_row}-name">Name:</label>
                                <input class="cell-input" type="text" id="row-${current_row}-name" name="row-${current_row}-name"/>
                            </div>
                            <div class="cell_part">
                                <label for="row-${current_row}-description">Description:</label>
                                <input class="cell-input" type="text" id="row-${current_row}-description" name="row-${current_row}-description"/>
                            </div>
                        </div>
                    </th>
                    <td id="row-${current_row}-cell-1" class="cell data-cell">
                        <div class="cell-wrapper">
                            <div class="cell_part">
                                <label for="row-${current_row}-cell-1-score">Score:</label>
                                <input class="cell-input" type="number" id="row-${current_row}-cell-1-score" name="row-${current_row}-cell-1-score"/>
                            </div>
                            <div class="cell_part">
                                <label for="row-${current_row}-cell-1-description">Description:</label>
                                <input class="cell-input" type="text" id="row-${current_row}-cell-1-description" name="row-${current_row}-cell-1-description"/> 
                            </div>
                        </div>
                    </td>
                    <td class="cell">
                        <button type="button" id="row-${current_row}-add-cell-button" class="add-cell-button">Add Cell</button>
                    </td>`);
    table.append(new_row);
    cell_counts.push(2);
    $(`#row-${current_row}-add-cell-button`).click(add_cell_callback);
    current_row++;

}

function add_cell_callback(event) {
    let new_cell = $("<td>");
    let row_number = event.target.id.split("-")[1];
    let cell_index = parseInt(row_number) - 1;
    let current_cell = cell_counts[cell_index];
    new_cell.attr('id', `row-${row_number}-cell-${current_cell}`);
    new_cell.addClass("cell");
    new_cell.addClass("data-cell");
    new_cell.html(`
            <div class="cell-wrapper">
                <div class="cell_part">
                    <label for="row-${row_number}-cell-${current_cell}-score">Score:</label>
                    <input class="cell-input" type="number" id="row-${current_row}-cell-${current_cell}-score" name="row-${current_row}-cell-${current_cell}-score"/>
                </div>   
                <div class="cell_part">
                    <label for="row-${current_row}-cell-${current_cell}-description">Description:</label>
                    <input class="cell-input" type="text" id="row-${current_row}-cell-${current_cell}-description" name="row-${current_row}-cell-${current_cell}-description"/>
                </div>
            </div>
        `);
    $(`#row-${row_number}-cell-${current_cell - 1}`).after(new_cell);
    cell_counts[cell_index]++;
    if (cell_counts[cell_index] > max_cells) scoreHeader.attr('colspan', cell_counts[cell_index]);
}



$(document).ready(() => {

    table = $(".rubric-edit-table");
    scoreHeader = $("#scoreHeader");

    $(".add-row-button").click(add_row_callback);
    $(".add-cell-button").click(add_cell_callback);

    $(".form").submit((event) => {

        $(".rubric_create_input").val(convert_to_json());

    });

});