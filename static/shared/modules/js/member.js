window.ModuleManager.registerModuleHandler("member", "activate", function () {
    var msg = window.ModuleManager.getMessage("member");
    if (msg) {
        $("#member-form input[name='ssn']").val(msg);
    }
})

window.ModuleManager.registerModuleHandler("member", "save", function () {
    let a = $("#member-form").serializeArray();
    let d = {};
    for (let x of a) {
        d[x.name] = x.value;
    }

    let g = /[0-9]/g;
    let ssn = d['ssn'].match(g).join("");
    string = JSON.stringify(d);
    d = {};
    d['data'] = string;
    window.Api.submitMember(d, function (msg) {
        window.ModuleManager.sendMessage("payment", ssn);
        window.ModuleManager.loadModule("payment");
        window.ModuleManager.saveSuccess("member", msg.result);
    });
})

window.ModuleManager.activateModule("member");

$("#member-form .form-kt").each(function () {
    new Cleave(this, {
        delimiter: '-',
        blocks: [6, 4]
    });
})


$(document).ready(function () {
    $(document).on('click', "#member-payer-kt-search", function (e) {
        e.stopPropagation();
        let kt = $(this).siblings(".form-kt").val();
        kt = kt.match(/\d+/g).join("");
        setMemberCandidate(kt);
    });

    function setMemberCandidate(kt) {
        window.Api.getPerson({ "ssn": kt }, function (e) {
            if (e.results.length == 0) {
                window.ModuleManager.requestData("member", "person", function (msg) {
                    var person = msg
                    $("#member-form input[name='pid']").val(person.pid);
                    $("#member-form input[name='name']").val(person.name);
                }, kt);
            }
            else {
                var person = e.results[0]
                $("#member-form input[name='pid']").val(person.pid);
                $("#member-form input[name='name']").val(person.name);
            }
        });
    }
})