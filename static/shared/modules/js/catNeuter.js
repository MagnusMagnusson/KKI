window.ModuleManager.registerModuleHandler("catNeuter", "activate", function () {
    var msg = window.ModuleManager.getMessage("catNeuter");
    if (msg) {
        type = "cat";
        id = msg;
        $("#catNeuterForm-id").val(id);
        data = { type, "values": { id } };
        window.Api.get(data, function (result) {
            $("#catNeuterForm-catRegNr").val(result.results.registry)
            $("#catNeuterForm-catName").val(result.results.name)
        })
    }
})

window.ModuleManager.registerModuleHandler("catNeuter", "save", function () {
    let a = $("#catNeuter-form").serializeArray();
    let d = {};
    for (let x of a) {
        d[x.name] = x.value;
    }
    string = JSON.stringify(d);
    d = {};
    d['data'] = string;
    window.Api.submitNeuter(d, function (msg) {
        window.ModuleManager.saveSuccess("catNeuter", msg.result, msg.result);
    });
})

window.ModuleManager.activateModule("catNeuter");


$(document).ready(function () {
    $(document).on('click', "#catNeuter-regnr-search", function (e) {
        e.stopPropagation();
        let kt = $(this).siblings("#catNeuterForm-catRegNr").val();
        data = {}
        data.registry = kt
        window.Api.getCat(data, function (result) {
            $("#catNeuterForm-catRegNr").val(result.results[0].registry)
            $("#catNeuterForm-id").val(result.results[0].id)
            $("#catNeuterForm-catName").val(result.results[0].name)
        })
    });
})