window.ModuleManager.registerModuleHandler("person", "activate", function () {
    var msg = window.ModuleManager.getMessage("person");
    if (msg) {
        $("#person-form input[name='ssn']").val(msg);
    }
})

window.ModuleManager.registerModuleHandler("person", "save", function () {
    let a = $("#person-form").serializeArray();
    let d = {};
    for (let x of a) {
        d[x.name] = x.value;
    }
    d['ssn'] = d['ssn'].match(/\d+/g).join("");
    string = JSON.stringify(d);
    d = {};
    d['data'] = string;
    window.Api.submitPerson(d, function (msg) {
        window.ModuleManager.saveSuccess("person",msg.result);
    });
})

window.ModuleManager.activateModule("person");

$("#person-form .form-kt").each(function () {
    new Cleave(this, {
        delimiter: '-',
        blocks: [6, 4]
    });
})

new Cleave("#person-form input[name='phone']", {
    delimiter: '-',
    blocks: [3, 4]
});