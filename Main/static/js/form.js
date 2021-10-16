$(document).ready(function (){
    if (document.referrer !== window.location.href) {
        window.sessionStorage.setItem('backUrl', document.referrer);
    }
    $(".form-main").submit(function (){
        $(".submit-button .loading").toggleClass('d-none', false);
        $(".submit-button .submit-word").toggleClass('d-none', true);
    });
    $(".back-button").click(function (){
        const backUrl = window.sessionStorage.getItem('backUrl');
        window.sessionStorage.removeItem('backUrl');
        window.location.replace(backUrl);
    });
});
