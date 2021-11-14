'use strict';

$(document).ready(function () {
    /**
     * This function will run when the document is loaded
     * It sets up the "back", "submit", and "show help" buttons
     */

    let form = $(".form-main");
    let back_button = $(".back-button");
    let help_button = $("#help-button");
    let help_label = $("#help-label");
    let help_shown = false;

    if (document.referrer !== window.location.href) {
        window.sessionStorage.setItem('backUrl', document.referrer);
    }
    form.submit(function () {
        /**
         * This function is run when the form is submitted
         * It shows the loading spinner and hides the text in the submit button
         */

        $(".submit-button .loading").toggleClass('d-none', false);
        $(".submit-button .submit-word").toggleClass('d-none', true);
    });
    back_button.click(function () {
        /**
         * This function is run when the back button is pressed
         * It goes back to the last page that is not this one
         */

        const backUrl = window.sessionStorage.getItem('backUrl');
        window.sessionStorage.removeItem('backUrl');
        window.location.replace(backUrl);
    });
    if ($(".field-help").length > 0) {
        help_button.toggleClass("d-none", false);
    }
    help_button.click(function () {
        /**
         * This function is run when the help button is pressed
         * It shows the help text for every field that has one
         */

        help_shown = !help_shown;
        help_label.text(help_shown ? "Hide Help" : "Show Help");
    });
});
