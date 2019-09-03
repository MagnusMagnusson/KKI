$(document).ready(function (e) {

    function addToOwnerList(person) {
        let list = $("#catteryOwner-list-window .list-window-element[data-value='" + person.pid + "']");

        if (list.length > 0) {
            $("li[data-value='" + person.pid + "']").animateHighlight("#dd0000", 5000);
        }
        else {
            let li = $("<li data-value = '" + person.pid + "' class='list-window-element'>" + person.name + "  -  <small>" + person.ssn + "</small> <span class='red'>X</span></li>")
            $("#catteryOwner-list-window ul").append(li);
        }
    }

    function addOwner(kt) {
        window.Api.getPerson({ "ssn": kt , 'member':true}, function (e) {
            if (e.results.length == 0) {
                alert("Enginn félagi hefur þessa kennitölu");
            }
            else {
                var person = e.results[0]
                addToOwnerList(person);
            }
        });
    }

    $(document).on('click', "#catteryOwner-kt-search", function (e) {
        e.stopPropagation();
        let kt = $(this).siblings(".form-kt").val();
        kt = kt.match(/\d+/g).join("");
        addOwner(kt);
    });

    $(document).on('click', "#catteryOwner-list-window .list-window-element .red", function (e) {
        e.stopPropagation();
        $(this).parents(".list-window-element")[0].remove();
    });

    window.ModuleManager.registerModuleHandler("catteryOwner", "activate", function () {
        let msg = window.ModuleManager.getMessage("catteryOwner");
        if (msg) {
            type = "cattery";
            id = msg;
            $("#catteryOwnerForm-id").val(id);
            data = { type, "values": { id } };
            window.Api.getById(data, function (result) {
                for (person of result.results.owners) {
                    addToOwnerList(person);
                }
            })
        }
    })

    window.ModuleManager.registerModuleHandler("catteryOwner", "save", function () {
        let d = {}
        d['id'] = $("#catteryOwnerForm-id").val();
        let owners = []
        $("#catteryOwner-list-window li").each(function (e) {
            owners.push($(this).data("value"));
        });
        d['owners'] = owners;
        string = JSON.stringify(d);
        d = {};
        d['data'] = string;
        window.Api.submitCattery(d, function (msg) {
            window.ModuleManager.saveSuccess("catteryOwner");
        });
    })

    window.ModuleManager.activateModule("catteryOwner");  

    $("#catteryOwner-form .form-kt").each(function () {
        new Cleave(this, {
            delimiter: '-',
            blocks: [6, 4]
        });
    })
});


