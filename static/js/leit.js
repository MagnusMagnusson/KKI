searchCallback = function (msg) {
    throw "SITE MUST IMPLEMENT searchCallback(msg);";
}

$(document).ready(function () {
    $("#leitarTakki").on("click", function (e) {
        var value = $("#leitargluggi").text();
        var type = $("#leitargluggi").data('type');
        var term = $("#leitargluggi").data('term');
        window.Api.find({ value,type,term }, searchCallback);
    });
})
