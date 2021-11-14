'use strict';

/**
 * This file is used when creating or editing a rubric
 */

let table = undefined;
let add_row = undefined;

function convert_from_json(src_json) {
    /**
     * This function loads JSON and shows it on the table
     * This is used when loading a non-empty Rubric for editing
     */

    add_row.click();

    if (src_json !== "[]") {

        let src_obj = JSON.parse(src_json);

        for (let i = 0; i < src_obj.length; i++) {

            let row = src_obj[i];
            let row_elem = $(table.find(".r_row").eq(i));
            row_elem.find(".row-name").val(row['name']);
            row_elem.find(".row-description").val(row['description']);

            for (let y = 0; y < row.cells.length; y++) {

                let cell = row.cells[y];
                let cell_elem = $(row_elem.children(".data-cell").eq(y));
                cell_elem.find(".cell-score").val(cell['score']);
                cell_elem.find(".cell-description").val(cell['description']);

                if (y !== row.cells.length - 1) row_elem.find(".add-cell-button").click();

            }

            if (i !== src_obj.length - 1) add_row.click();

        }

    }

}

function convert_to_json() {
    /**
     * This function converts the table into JSON to send to the backend
     */

    let new_rubric = [];

    table.find(".r_row").each(function (index, object) {

        let new_row = {
            "name": $(object).find(".row-name").val(),
            "description": $(object).find(".row-description").val(),
            "cells": []
        };

        $(object).children(".data-cell").each(function (index, cell) {

            let new_cell = {
                "score": parseFloat($(cell).find(".cell-score").val()),
                "description": $(cell).find(".cell-description").val()
            };
            new_row["cells"].push(new_cell);

        });

        new_rubric.push(new_row);

    });

    console.log(new_rubric);

    return JSON.stringify(new_rubric);

}

function delete_row_callback(event) {
    /**
     * This function is run when the "Delete" button is clicked on a row
     *  It deletes the row.
     */

    $(event.target).parents("tr").remove();

}

function delete_cell_callback(event) {
    /**
     * This function is run when the "Delete" button is clicked on a cell
     *  It deletes the cell
     */

    $(event.target).parents("td").remove();

}

function add_row_callback() {
    /**
     * This function is run to add a row to the table, it loads HTML from the template div
     */

    let new_row = $("<tr>");
    new_row.addClass("r_row");
    new_row.html($("#templates #row-template").html());
    table.append(new_row);
    new_row.find(".add-cell-button").click(add_cell_callback);
    new_row.find(".add-cell-button").click();
    new_row.find(".delete-row").click(delete_row_callback);
    new_row.find(".delete-cell").click(delete_cell_callback);
}

function add_cell_callback(event) {
    /**
     * This function is used to add a cell to a row, it loads HTML from the template div
     */

    let new_cell = $("<td>");
    new_cell.addClass("cell");
    new_cell.addClass("data-cell");
    new_cell.addClass("p-1");
    new_cell.html($("#templates #cell-template").html());
    $(event.target).parent().before(new_cell);
    new_cell.find(".delete-cell").click(delete_cell_callback);
}

function submit_callback() {
    /**
     * This function is run when the form is submitted.
     * It ensures that the JSON is sent to the backend.
     */

    $(".rubric_create_input").val(convert_to_json());

}


$(document).ready(() => {
    /**
     * This function is run when the document has been loaded successfully.
     * It sets up some variables and callbacks.
     */

    table = $(".rubric-editing tbody");
    add_row = $(".add-row-button");

    add_row.click(add_row_callback);
    $(".add-cell-button").click(add_cell_callback);
    $(".delete-row").click(delete_row_callback);
    $(".delete-cell").click(delete_cell_callback);

    $(".form").submit(submit_callback);

    convert_from_json($(".rubric_create_input").val());

});