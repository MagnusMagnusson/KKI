$(document).ready(function (e) {
    let owners = [];
    let keyCodes = {}
    function addOwner(kt) {
        window.Api.getPerson({ "ssn": kt , 'member':true}, function (e) {
            if (e.results.length == 0) {
                alert("Enginn félagi hefur þessa kennitölu");
            }
            else {
                var person = e.results[0]
                if (owners.includes(person.id)) {
                    $("li[data-value='" + keyCodes[person.id] + "']").animateHighlight("#dd0000", 5000);
                }
                else {
                    owners.push(person.id);
                    keyCodes[person.id] = Math.floor(Math.random() * Math.pow(2, 31));
                    let li = $("<li data-value = '" + keyCodes[person.id]+ "' class='list-window-element'>" + person.name + "  -  <small>" + person.ssn + "</small></li>")
                    $("#cattery-list-window ul").append(li);
                }
            }
        });
    }

    $(document).on('click', "#cattery-kt-search", function (e) {
        e.stopPropagation();
        let kt = $(this).siblings(".form-kt").val();
        kt = kt.match(/\d+/g).join("");
        addOwner(kt);
    });

    window.ModuleManager.registerModuleHandler("cattery", "activate", function () {
        $('[name="date"]').val(new Date().toISOString().split('T')[0]);
    })

    window.ModuleManager.registerModuleHandler("cattery", "save", function () {
        let a = $("#cattery-form").serializeArray();
        let d = {}
        for (let x of a) {
            d[x.name] = x.value;
        }
        d['owners'] = owners;
        window.Api.create("catteries", d, function (msg) {
            window.ModuleManager.saveSuccess("cattery");
        });
    })

    window.ModuleManager.activateModule("cattery");  

    $("#cattery-form .form-kt").each(function () {
        new Cleave(this, {
            delimiter: '-',
            blocks: [6, 4]
        });
    })
});


