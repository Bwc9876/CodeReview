$(document).ready(() => {

    const rubricDropdown = $("#id_rubric");
    const previewButton = $("#rubricPreviewButton");

    rubricDropdown.change(() => previewButton.attr("disabled", rubricDropdown.val() === ""));

    previewButton.click(() => {
        $(".rubric-preview").toggleClass("d-none", true);
        $(`#rubric-${rubricDropdown.val()}`).toggleClass("d-none", false);
    });
});