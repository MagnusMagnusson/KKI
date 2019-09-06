searchCallback = function (msg) {
    throw "SITE MUST IMPLEMENT searchCallback(msg);";
}

$(document).ready(function () {
    $("#leitarTakki").on("click", function (e) {
        var value = $("#leitargluggi").text();
        var type = $("#leitargluggi").data('type');
        var term = $("#leitargluggi").data('term');
        console.log(term);
        var search = {}
        search[term] = value;
        window.Api.find(type, search, searchCallback);
    });
})
