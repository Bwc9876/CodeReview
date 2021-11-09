function cleanupSubmitClick() {
    $("#cleanupSpinner").toggleClass("d-none", false);
    $("#cleanupSubmitText").toggleClass("d-none", true);
    $("#cleanupForm").submit();
}

$(document).ready(function (){
    $("#cleanupSubmitButton").click(cleanupSubmitClick);
});