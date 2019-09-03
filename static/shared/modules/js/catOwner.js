$(document).ready(function (e) {

    function addToOwnerList(person) {
        let list = $("#catOwner-list-window .list-window-element[data-value='" + person.pid + "']");

        if (list.length > 0) {
            $("li[data-value='" + person.pid + "']").animateHighlight("#dd0000", 5000);
        }
        else {
            let li = $("<li data-value = '" + person.pid + "' class='list-window-element'>" + person.name + "  -  <small>" + person.ssn + "</small> <span class='red'>X</span></li>")
            $("#catOwner-list-window ul").append(li);
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

    $(document).on('click', "#catOwner-kt-search", function (e) {
        e.stopPropagation();
        let kt = $(this).siblings(".form-kt").val();
        kt = kt.match(/\d+/g).join("");
        addOwner(kt);
    });

    $(document).on('click', "#catOwner-list-window .list-window-element .red", function (e) {
        e.stopPropagation();
        $(this).parents(".list-window-element")[0].remove();
    });

    window.ModuleManager.registerModuleHandler("catOwner", "activate", function () {
        let msg = window.ModuleManager.getMessage("catOwner");
        if (msg) {
            type = "cat";
            id = msg;
            $("#catOwner-id").val(id);
            data = { type, "values": {id} };
            window.Api.getById(data, function (result) {
                for (person of result.results.owners) {
                    addToOwnerList(person);
                }
            })
        }
    })

    window.ModuleManager.registerModuleHandler("catOwner", "save", function () {
        let a = $("#catOwner-form").serializeArray();
        let d = {};
        for (let x of a) {
            d[x.name] = x.value;
        }

        let owners = []
        $("#catOwner-list-window li").each(function (e) {
            owners.push($(this).data("value"));
        });
        d['owners'] = owners;
        string = JSON.stringify(d);
        d = {};
        d['data'] = string;
        window.Api.submitCatOwner(d, function (msg) {
            window.ModuleManager.saveSuccess("catOwner",msg.results,msg.results);
        });
    })

    window.ModuleManager.activateModule("catOwner");  

    $("#catOwner-form .form-kt").each(function () {
        new Cleave(this, {
            delimiter: '-',
            blocks: [6, 4]
        });
    })
});


