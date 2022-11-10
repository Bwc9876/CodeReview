$(document).ready(() => {
    const rubricDropdown = $("#id_rubric");
    const previewButton = $("#rubricPreviewButton");
    const checkForSelected = () => previewButton.attr("disabled", rubricDropdown.val() === "");
    checkForSelected();
    rubricDropdown.change(checkForSelected);
    previewButton.click(() => {
        $(".rubric-preview").toggleClass("d-none", true);
        $(`#rubric-${rubricDropdown.val()}`).toggleClass("d-none", false);
    });
});