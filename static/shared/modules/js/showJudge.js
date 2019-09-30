$(document).ready(function (e) {
    let name, country, judges, show;
    judges = [];
    $(document).on('input',"#showJudge_judgename", function (e) {
        e.stopPropagation();
        $("#showJudge_id").val("");
        let text = $("#showJudge_judgename").val();
        if (text.length < 3) {
            $("#showJudge_search_wrapper .result-box").hide();
            return;
        }
        window.Api.find("judge", { "name": text }, function (e) {
            let list = $("#showJudge_search_wrapper .result-box .result-box-list");
            $(list).empty();
            i = 0;
            for (let x of e.results.slice(0, 10)) {
                let li = $(`<li>${x.name} [${x.country}] </li>`);
                $(list).append(li);

                $(li).on("click touchstart", function (e) {
                    e.preventDefault();
                    $("#showJudge_id").val(x.judge_id);
                    $("#showJudge_judgename").val(x.name);
                    $("#showJudge-country").val(x.country);
                    $("#showJudge_search_wrapper .result-box").hide();
                });
            }
            $("#showJudge_search_wrapper .result-box").show();

        });
    });

    $(document).on('click touchstart', "#addJudge-button", function (e) {
        let id = $("#showJudge_id").val();
            name = $("#showJudge_judgename").val();
            country = $("#showJudge-country").val();
        if (!id || id == "") { //The currently selected person does not exist.
            if (name.length < 3) {
                return;
            }
            d = { "name": name, "country": country };
            window.Api.find("person", d, function (result) {
                $("#showJudge-new-judge-list").empty();
                for (let person of result.results) {
                    let judge;
                    if (person.is_judge) {
                        judge = "(Dómari)"
                    } else {
                        judge = ""
                    }
                    let li = `<li class="showJudge-new-judge-list-element" data-person = "${person.id}">${person.name} [${person.country}] ${judge}</li>`;
                    $("#showJudge-new-judge-list").append(li);
                }
                $("#confirm-judge-name").text(name);
                $("#confirm-judge-nation").text(country);
                $("#showJudge-form").hide();
                $("#confirm-new-judge").show();
            });
        } else {
            addToJudgeList(id, name, country);
        }
    });

    $(document).on('click', "#showJudge-list-window .list-window-element .red", function (e) {
        e.stopPropagation();
        let dad = $(this).parents(".list-window-element")[0];
        let id = $(dad).data("value");
        let index = judges.indexOf(id);
        judges.splice(index, 1);
        $(dad).remove();
    });

    $(document).on("click", ".showJudge-new-judge-list-element", function (e) {
        if ($(this).data("judge")) {
            addToJudgeList($(this).data("jid"), $(this).data("name"), $(this).data("country"));
            swapPane();
        } else {
            d = { "is_judge": true }
            window.Api.edit("person", d, function (per) {
                per = per.results;
                addToJudgeList(per.judge_id, per.name, per.country);
                swapPane();
            }, [$(this).data(id)]);
        }
    });

    $(document).on("click", "#confirmJudge-yes", function (e) {
        let d = { "name": name, "country": country };
        window.Api.create("judge", d, function (judge) {
          judge = judge.results;
          addToJudgeList(judge.judge_id, judge.name, judge.country);
          swapPane();
       });
    });

    $(document).on("click", "#confirmJudge-no", function (e) {
        swapPane();
    });

    function addToJudgeList(id, name, country) {
        judges.push(id);
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
            show = msg;
        }
        name = "";
        judge = [];
        country = "";
        $("#showJudge_id").val(null);
        $("#showJudge_judgename").val("");
        swapPane();
        window.Api.get("show", {}, function (show) {
            for (let judge of show.results.judges) {
                window.Api.get("judge", {}, function (judge) {
                    judge = judge.results;
                    addToJudgeList(judge.judge_id, judge.name, judge.country);
                }, [judge]);
            }
        }, [show]);
    })

    window.ModuleManager.registerModuleHandler("showJudge", "save", function () {
        for (let i = 0; i < judges.length; i++) {
            judges[i] = parseInt(judges[i]);
        }
        d = { "judges": judges }
        window.Api.edit("show", d, function (show) {
            name = "";
            judges = [];
            country = "";
            window.ModuleManager.saveSuccess("showJudge",show.results, show.results);
        }, [show])
    })

    window.ModuleManager.activateModule("showJudge");  

    function swapPane() {
            $("#showJudge-form").show();
            $("#confirm-new-judge").hide();
    }

});

