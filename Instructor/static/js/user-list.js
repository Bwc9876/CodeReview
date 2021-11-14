'use strict';

/* This file is used in the user list page for user cleanup */

function cleanupSubmitClick() {
    /**
     * This function will run when the submit button in the user cleanup modal is pressed.
     * It shows the spinner in the button and submits the form.
     */

    $("#cleanupSpinner").toggleClass("d-none", false);
    $("#cleanupSubmitText").toggleClass("d-none", true);
    $("#cleanupForm").submit();
}

$(document).ready(function () {
    /**
     * This function will run when the document has loaded
     * It sets up the cleanupSubmit button's click callback.
     */

    $("#cleanupSubmitButton").click(cleanupSubmitClick);
});
