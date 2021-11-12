$(document).ready(function (){
    /**
     * This function will run when the document loads.
     * It sets the title of the page to whatever is in the #pageHeader element.
     * It also falls back to light theme in case the browser doesn't support prefers-color-scheme
     */

    document.title = `${$("#pageHeader").text()} | CodeReview`;
    if (window.matchMedia(`(prefers-color-scheme: light)`).media === "not all") {
        $("#light-theme-css").attr('media', "screen")
    }
});
