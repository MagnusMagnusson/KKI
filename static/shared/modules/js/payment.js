$(document).ready(function (e) {

    function setPayingMember(kt) {
        window.Api.getPerson({ "ssn": kt }, function (e) {
            if (e.results.length == 0) {
                window.ModuleManager.requestData("payment", "person", function (msg) {
                    var person = msg
                    $("input[name='pid']").val(person.pid);
                    $("input[name='name']").val(person.name);
                }, kt);
            }
            else {
                var person = e.results[0]
                $("input[name='pid']").val(person.pid);
                $("input[name='name']").val(person.name);
            }
        });
    }

    window.ModuleManager.registerModuleHandler("payment", "activate", function () {
        $('[name="date"]').val(new Date().toISOString().split('T')[0]);

        let ktSnoop = $("[name='profile-kt']");
        if (ktSnoop.length > 0) {
            var ssn = $(ktSnoop).data('kt');
            $("[name='ssn']").val(ssn);
            setPayingMember(ssn);

        }
    })

    window.ModuleManager.registerModuleHandler("payment", "save", function () {
        let a = $("#payment-form").serializeArray();
        let d = {}
        for (let x of a) {
            d[x.name] = x.value;
        }
        let dependancies = []
        $("#payment-list-window li").each(function (e) {
            dependancies.push($(this).data("value"));
        });
        d['dependancies'] = dependancies;
        string = JSON.stringify(d);
        d = {};
        d['data'] = string;
        window.Api.submitPayment(d, function (msg) {
            window.ModuleManager.saveSuccess("payment");
        });
    })

    window.ModuleManager.activateModule("payment");

    $(document).on('click', "#payment-kt-search", function (e) {
        e.stopPropagation();
        let kt = $(this).siblings(".form-kt").val();
        kt = kt.match(/\d+/g).join("");
        window.Api.getPerson({ "ssn": kt }, function (e) {
            if (e.results.length == 0) {
                window.ModuleManager.requestData("payment", "person", function (msg) {
                    var person = msg;
                    let list = $("#payment-list-window .list-window-element[data-value='" + person.pid + "']");
                    if (list.length > 0) {
                        $("li[data-value='" + person.pid + "']").animateHighlight("#dd0000", 5000);
                    }
                    else {
                        let li = $("<li data-value = '" + person.pid + "' class='list-window-element'>" + person.name + "  -  <small>" + person.ssn + "</small></li>")
                        $("#payment-list-window ul").append(li);
                    }
                },kt);
            }
            else {
                var person = e.results[0]
                let list = $("#payment-list-window .list-window-element[data-value='" + person.pid+"']");
                if (list.length > 0) {
                    $("li[data-value='" + person.pid +"']").animateHighlight("#dd0000", 5000);
                }
                else {
                    let li = $("<li data-value = '" + person.pid + "' class='list-window-element'>" + person.name + "  -  <small>" + person.ssn + "</small></li>")
                    $("#payment-list-window ul").append(li);
                }
            }
        });
    });

    $(document).on('click', "#payment-payer-kt-search", function (e) {
        e.stopPropagation();
        let kt = $(this).siblings(".form-kt").val();
        kt = kt.match(/\d+/g).join("");
        setPayingMember(kt);
    });

    

    $("#payment-form .form-kt").each(function () {
        new Cleave(this, {
            delimiter: '-',
            blocks: [6, 4]
        });
    })
});


