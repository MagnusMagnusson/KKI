$(document).ready(function (e) {
    $(document).on('input',"#showJudge_judgename", function (e) {
        e.stopPropagation();
        $("#showJudge_id").val("");
        let text = $("#showJudge_judgename").val();
        if (text.length < 3) {
            $("#showJudge_search_wrapper .result-box").hide();
            return;
        }
        window.Api.find({ 'type': 'judge', 'term': 'name', 'value': text }, function (e) {
            let list = $("#showJudge_search_wrapper .result-box .result-box-list");
            $(list).empty();
            i = 0;
            for (let x of e.results.slice(0, 10)) {
                let li = $(`<li>${x[1].name} [${x[1].country}] </li>`);
                $(list).append(li);

                $(li).on("click touchstart", function (e) {
                    e.preventDefault();
                    $("#showJudge_id").val(x[1].jid);
                    $("#showJudge_judgename").val(x[1].name);
                    $("#showJudge-country").val(x[1].country);
                    $("#showJudge_search_wrapper .result-box").hide();
                });
            }
            $("#showJudge_search_wrapper .result-box").show();

        });
    });

    $(document).on('click touchstart', "#addJudge-button", function (e) {
        let id = $("#showJudge_id").val();
            let name = $("#showJudge_judgename").val();
            let country = $("#showJudge-country").val();
        if (!id || id == "") { //The currently selected person does not exist.
            console.log(id);
            if (name.length < 3) {
                return;
            }
            d = { "type": "person", term: "name", "value": name }
            api.ge
        } else {
            addToJudgeList(id, name, country);
        }
    });

    $(document).on('click', "#showJudge-list-window .list-window-element .red", function (e) {
        e.stopPropagation();
        $(this).parents(".list-window-element")[0].remove();
    });


    function addToJudgeList(id,name,country) {
        let list = $("#showJudge-list-window .list-window-element[data-value='" + id + "']");

        if (list.length > 0) {
            $("li[data-value='" + id + "']").animateHighlight("#dd0000", 5000);
        }
        else {
            let li = $("<li data-value = '" + id + "' class='list-window-element'>" + name + "  - [" + country + "] <span class='red'>X</span></li>")
            $("#showJudge-list-window ul").append(li);
        }
    }

    window.ModuleManager.registerModuleHandler("showJudge", "activate", function () {
        let msg = window.ModuleManager.getMessage("showJudge");
        if (msg) {
            $("#show-id").val(msg);
        }
    })

    window.ModuleManager.registerModuleHandler("showJudge", "save", function () {
        /*let a = $("#showJudge-form").serializeArray();
        let d = {}
        for (let x of a) {
            d[x.name] = x.value;
        }

        string = JSON.stringify(d);
        d = {};
        d['data'] = string;
        window.Api.submitShow(d, function (msg) {
            window.ModuleManager.saveSuccess("show",msg,msg);
        });*/
    })

    window.ModuleManager.activateModule("showJudge");  

});


