$(document).ready(function (e) {
    var owners = [];
    var keyCodes = {};
    var id = null;
    function addToOwnerList(person) {
        if (owners.includes(person.id)) {
            $("li[data-value='" + keyCodes[person.id] + "']").animateHighlight("#dd0000", 5000);
        }
        else {
            let key = Math.floor(Math.random() * Math.pow(2, 32));
            owners.push(person.id);
            keyCodes[person.id] = key;
            let li = $("<li data-value = '" + key + "' class='list-window-element'>" + person.name + "  -  <small>" + person.ssn + "</small> <span class='red'>X</span></li>")
            $("#catteryOwner-list-window ul").append(li);
        }
    }

    function addOwner(kt) {
        window.Api.get("person", { "ssn": kt , 'member':true}, function (e) {
            if (e.length == 0) {
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
        let key = $($(this).parents(".list-window-element")[0]).data("value");
        let deadOwner = null;
        for (let o of owners) {
            if (keyCodes[o] === key) {
                deadOwner = o;
            }
        }
        if (deadOwner) {
            owners.splice(owners.indexOf(deadOwner, 1));
            delete keyCodes[deadOwner];
        }
        $(this).parents(".list-window-element")[0].remove();
    });

    window.ModuleManager.registerModuleHandler("catteryOwner", "activate", function () {
        let msg = window.ModuleManager.getMessage("catteryOwner");
        if (msg) {
            id = msg;
            $("#catteryOwnerForm-id").val(id);
            window.Api.get("cattery", {}, function (result) {
                console.log(result.results)
                for (person of result.results.owners) {
                    window.Api.get("person", {}, function (person) {
                        addToOwnerList(person.results);
                    }, null, [person])
                }
            }, null, [id])
        }
    })

    window.ModuleManager.registerModuleHandler("catteryOwner", "save", function () {
        let d = {}
        d['owners'] = owners;
        window.Api.edit("cattery", d, function (msg) {
            window.ModuleManager.saveSuccess("catteryOwner");
        }, null, [id]);
    })

    window.ModuleManager.activateModule("catteryOwner");  

    $("#catteryOwner-form .form-kt").each(function () {
        new Cleave(this, {
            delimiter: '-',
            blocks: [6, 4]
        });
    })
});


