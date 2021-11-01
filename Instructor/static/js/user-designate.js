'use strict';

/**
 * This JS file is used in the user-list page
 */

function formSaveCallback() {
    /**
     * This function is run when the form is saved, it fills out the session-input field with the proper JSON
     */

    let newObj = {"AM": [], "PM": []};
    $(".AM-session").children("tr").each((index, object) => {
        newObj["AM"].push($(object).children("th").attr('id'));
    });
    $(".PM-session").children("tr").each((index, object) => {
        newObj["PM"].push($(object).children("th").attr('id'));
    });
    $(".session-input").val(JSON.stringify(newObj));
}

$(document).ready(function () {
    /**
     * This function is run when the document has successfully loaded
     * It initializes the Sortable library and sets up the form's save callback
     */

    const options = {
        group: "sessions",
        animation: 150,
        multiDrag: true,
        selectedClass: "bg-light",
        fallbackTolerance: 3,
        ghostClass: "bg-light",
    };

    $(".AM-session").sortable(options);

    $(".PM-session").sortable(options);

    $(".session-form").submit(formSaveCallback);
    formSaveCallback();

});
