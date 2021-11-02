$(document).ready(function () {
    /**
     * This function will run when the document is loaded.
     * It sets up the "back", "submit", and "show help" buttons.
     */

    let form = $(".form-main");
    let back_button = $(".back-button");
    let help_button = $("#help-button");
    let help_label = $("#help-label")
    let help_shown = false;

    if (document.referrer !== window.location.href) {
        window.sessionStorage.setItem('backUrl', document.referrer);
    }
    form.submit(function () {
        $(".submit-button .loading").toggleClass('d-none', false);
        $(".submit-button .submit-word").toggleClass('d-none', true);
    });
    back_button.click(function () {
        const backUrl = window.sessionStorage.getItem('backUrl');
        window.sessionStorage.removeItem('backUrl');
        window.location.replace(backUrl);
    });
    if ($(".field-help").length > 0) {
        help_button.toggleClass("d-none", false);
    }
    help_button.click(function(){
        help_shown = !help_shown;
        help_label.text(help_shown? "Hide Help" : "Show Help");
    });
});
