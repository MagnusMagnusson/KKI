$(document).ready(function (e) {
 

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

    window.ModuleManager.registerModuleHandler("showAward", "activate", function () {
        alert("Active");
    })

    window.ModuleManager.registerModuleHandler("showAward", "save", function () {
        alert("LOL");
    })

    window.ModuleManager.activateModule("showAward");  

});


