function formSaveCallback(){
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

    const options = {
        group: "sessions",
        animation: 150,
        multiDrag: true,
        selectedClass: "selected-user",
        fallbackTolerance: 3,
        ghostClass: "hover-user"
    };

    $(".AM-session").sortable(options);

    $(".PM-session").sortable(options);

    $(".session-form").submit(formSaveCallback);
    formSaveCallback();

});
