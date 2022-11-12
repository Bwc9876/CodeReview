'use strict';

/**
 * This file is used when grading a rubric.
 */

function loadFromScoresArray(scores) {
    /**
     * This function loads the scores array into the table.
     */

    if (scores.length === 0) return;

    for (let i = 0; i < scores.length; i++) {
        const score = scores[i];
        if (score === -1) continue;
        const selector = `.criteria#grade-row-${i} .score-select[value="${score % 1 === 0 ? score.toFixed(1) : score}"]`;
        const cell = $(selector);
        cell.prop("checked", true);
    }
}

function update_cell_colors() {
    /**
     * This function updates cells that are selected with the CSS class of 'selected'.
     */

    $(".rubric-grading td.cell").each(function (index, object) {
        $(object).toggleClass("selected", $(object).children("label").children("input:checked").length > 0);
    });
}

function get_scores() {
    /**
     * This function gets the scores from the table.
     */

    const scores = [];
    $(".rubric-grading tr").each(function (index, object) {
        if (index === 0) return; // Skip the header row
        const score = $(object).find("input:checked").val();
        scores.push(score === undefined ? -1 : parseInt(score));
    });
    return scores;
}

function update_scores_input(scores) {
    /**
     * This function updates the 'scores' field with the proper JSON.
     */

    $(".rubric_grade_input").val(`[${scores.join(',')}]`);
}

function get_max(row_index) {
    /**
     * This function gets the max score of a row given its index.
     */

    return parseFloat($(`.criteria#grade-row-${row_index} .max-score-val`).text());
}

function update_total_score(scores) {
    /**
     * This function updates the label that displays the total score.
     */

    const report = $("#grade_report");
    let report_lst = [];
    let total = 0;
    let max = 0;
    for (let i = 0; i < scores.length; i++) {
        let score = scores[i];
        total += score;
        max += get_max(i);
    }
    report_lst[0] = `Grade: ${total.toFixed(1)}`;
    report_lst[1] = max.toFixed(1);
    report.text(report_lst.join('/'));
}

function score_button_callback() {
    /**
     * This function is run when a button within a cell is clicked, it updates the cell colors, totals, and JSON.
     */

    let scores = get_scores();
    update_cell_colors();
    update_scores_input(scores);
    update_total_score(scores);
}

function score_cell_callback(event) {
    /**
     * This function is run when a cell is clicked, it clicks the button within the cell.
     * This is for the sake of convenience as clicking a small button in the cell can get annoying.
     */

    $(event.target).children('label').children(".score-select").click();
}

$(document).ready(function () {

    /**
     * This function runs when the document has been loaded successfully,
     * It sets up callbacks.
     */

    $(".score-select").click(score_button_callback);
    $(".cell").click(score_cell_callback);
    loadFromScoresArray(JSON.parse($(".rubric_grade_input").val()));
    $(".score-select:checked").each((index, object) => {
        /**
         * This function clicks buttons that are checked so that way colors and totals are updated.
         */
        $(object).click();
    });
});

