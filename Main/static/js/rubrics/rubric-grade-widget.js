'use strict';

function get_scores(){
    let scores = [];
    $(".gradable-rubric .criteria input:checked").each(function(index, object) {
        scores.push(parseFloat($(object).val()));
    });
    return scores;
}

function update_scores_input(scores) {
    $(".rubric_grade_input").val(scores.join(','));
}

function get_max(row_index) {
    return parseFloat($(`.criteria#grade-row-${row_index} .max-score-val`).text());
}

function update_total_score(scores) {
    const report = $("#grade_report");
    let report_lst = report.text().split("/")
    let total = 0;
    let max = 0;
    scores.forEach(score => {
        total += score === -1? 0 : score;
        max += score === -1? 0 : get_max(scores.indexOf(score));
    });
    report_lst[0] = `Grade: ${total.toFixed(1)}`;
    report_lst[1] = max.toFixed(1);
    report.text(report_lst.join('/'));
}

function score_button_callback(event) {
    let scores = get_scores();
    update_scores_input(scores);
    update_total_score(scores);
}

function cell_click_callback(event){
    $(event.target).children("input").click();
}

function  loadCallback(event){
    $(".score-select").click(score_button_callback);
    $(".cell").click(cell_click_callback);
}

$(document).ready(loadCallback);

