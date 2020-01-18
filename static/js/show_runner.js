(function () {
let show_date;
$(document).ready(function () {
    init();
    handlers();
});

function handlers() {
    $("#judgement-form-abs").change(function () {
        if (this.checked) {
            judgement_lockout(true);
        } else {
            judgement_lockout(false);
        }
    });
    $(".sidebar-link").on("click touchstart", function (e) {
        $(".main-section").hide();
        newSection = $(this).data("section")
        $("#section-" + newSection).show();
        updateData(newSection);
    });
    $(document).on("click touchstart", ".judge-abs-list li", abs_remove_entry_handler);
    $(document).on("click touchstart", "#button-confirm-abs", abs_press_button_handler);
    $(document).on("change", "#nomination-form-categories", nomination_change_category);
    $(document).on("change", "#nomination-form-judge", nomination_change_judge);
    $(document).on("focusout", ".nomination-field", nomination_save_field);
    $(document).on("change", "#finals-form-categories", finals_change_category);
    $(document).on("change", ".finals-nomination-bis", finals_toggle_bis);
    $("#color-cat-id").on("focusout", colorGetEntrant);
    $('#color-cat-id').keyup(function (e) {
        if (e.keyCode == 13) {
            $(this).blur()
        }
    });
    $("#button-confirm-color").on("click touchstart", colorSaveEntrant);
    $("#judgement-save-button").on("click touchstart", judgement_save);
    $("#judgement-cat-id").on("focusout", judgementGetEntrant);
    $('#judgement-cat-id').keyup(function (e) {
        if (e.keyCode == 13) {
            $(this).blur()
        }
    });
    $(".files_settings_checkbox").on("change", function (a) {
        let aye = $(this).parents(".files_checkbox_wrapper").find("input[type='checkbox']:checked").length
        let no = $(this).parents(".files_checkbox_wrapper").find("input[type='checkbox']:not(:checked)").length
        let dad = $(this).parents(".files_settings_wrapper").find(".files_settings_all")[0];
        if (aye == 0) {
            $(dad).prop("indeterminate", false);
            $(dad).prop("checked", false);
        } else if (no == 0) {
            $(dad).prop("indeterminate", false);
            $(dad).prop("checked", true);
        } else {
            $(dad).prop("indeterminate", true);
        }
    });
    $(".files_settings_all").on("change", function (e) {
        let check = $(this).prop("checked")
        $(this).parent(".files_settings_wrapper").find(".files_settings_checkbox").prop("checked", check);
        
    });
    $("#files-save-button").on("click touchstart", files_get_file)
    $(".files_link").on("click touchstart", function (e) {
    $(".files_link").removeClass("selected");
        $(this).addClass("selected");
        let d = $(this).data("file");
        switch (d) {
            case "cage": {
                file = "/api/syningar/" + ENV.show + "/skjol/buramidar.pdf";
                fileName = "buramidar.pdf";
                break;
            }
            case "judge": {
                file = "/api/syningar/" + ENV.show + "/skjol/urslitablad.pdf";
                fileName = "urslitablad.pdf";
            }
        
        }
    })
}

    let _judges = {}
function init() {
    updateData("overview");
    window.Api.get("show", {}, function (show) {
        show = show.results;
        show_date = show.date;
        for (let judge_id of show.judges) {
            window.Api.get("judge", {}, function (judge) {
                judge = judge.results;
                _judges[judge_id] = judge;
            }, null, [judge_id])
        }
    }, null, [ENV.show]);

    $(".textinput").val("");
    $("input").prop("checked", false);

    $("#files_settings input[type='checkbox']").prop("checked", true);

}
function updateData(section) {
    switch (section) {
        case "overview": {
            $("#overview-judgementless-list").empty();
            $("#overview-judged-list").empty();
            let li = "<li>Sæki...</li>";
            $(li).appendTo("#overview-judged-list");
            $(li).appendTo("#overview-judgementless-list");
            d = {
                "judgement_ready": false
            }
            window.Api.getAll("entry", d, function (entries) {
                $("#overview-judgementless-list").empty();

                entries = entries.results;
                entries.sort(function (a, b) { return a.catalog_number - b.catalog_number; });
                for (let entry of entries) {
                    let catalog = entry.catalog_number;
                    let l = `<li><b>${catalog}</b></li>`;
                    $(l).appendTo("#overview-judgementless-list")
                }
            }, null, [ENV.show]);

            d = {
                "judgement_ready": true
            }
            window.Api.getAll("entry", d, function (entries) {
                $("#overview-judged-list").empty();
                entries = entries.results;
                entries.sort(function (a, b) { return a.catalog_number - b.catalog_number; });
                for (let entry of entries) {
                    let catalog = entry.catalog_number;
                    let cert = entry.recieved_certification ? "CERT":"";
                    let judgement = entry.judgement;
                    let nom = entry.nominations.length;
                    nom = nom > 0 ? " Tilnefndur("+nom+")" : "";
                    let l = `<li><b>${catalog}</b> ${judgement} ${cert} ${nom}</li>`;
                    $(l).appendTo("#overview-judged-list")
                }
            }, null, [ENV.show]);
            break;
        }
        case "abs": {
            $(".judge-abs-list").empty();
            d = { "was_absent": true }

            window.Api.get("entry", d, function (msg) {
                //We have obtained all our ABS cats. Fill in the details themselves. 
                if (msg.success) {
                    for (let entry of msg.results) {
                        let j = entry.judge;
                        let e = entry.catalog_number;
                        //Fetch their names
                        absAddToList(entry.cat, e, j);
                    }
                } else {
                    alert("Error");
                }
            }, null, [ENV.show]);
            break;
        }
        case "nominations": {
            let e = $("#nomination-form-judge")
            $(e).val("null");
            nomination_change_judge();
            break;
        }
        case "finals": {
            $(".finals-nomination-list").empty();
            finalNominations = {};
            finalasyncRequests = {};
            $(".finals-category-div").hide();
            $(".finals-please-wait").show();
            let judgeCache = {}
            window.Api.getAll("nomination", {}, function (nominations) {
                let noms = nominations.results;
                let done = 0;
                let total = noms.length;
                $(".finals-percent").text(`${done}/${total} sótt (${Math.floor(100 * done / total)}%)`);
                for (let nomination of noms) {
                    let uri = nomination.id;
                    let entry = nomination.entry;
                    let cat = nomination.cat;
                    let judge_id = nomination.judge;
                    let checked = (nomination.bis) ? "checked='checked'" : "";
                    let asyncId = Math.floor(1000000 * Math.random());
                    while (finalNominations[asyncId]) {
                        asyncId = Math.floor(1000000 * Math.random());
                    }
                    finalasyncRequests[asyncId] = true;
                    window.Api.get("cat", {}, function (cat) {
                        if (!finalasyncRequests[asyncId]) {
                            //New request data; abort.
                            return;
                        }
                        let randInt = Math.floor(1000000 * Math.random());
                        while (finalNominations[randInt]) {
                            randInt = Math.floor(1000000 * Math.random());
                        }
                        cat = cat.results;
                        let ems = cat.ems;
                        let bday = cat.birthdate;
                        let age = getAgeString(bday, show_date);
                        let name;
                        let addNom = function () {
                            let li = `
                                    <li class="finals-nomination-li">
                                        <input ${checked} class="finals-nomination-bis" data-id="${randInt}" id="finals-nomination-bis-${randInt}" type="checkbox">
                                        <span><b>${entry}</b></span>
                                        <span>${ems}</span>
                                        <span>${age} / ${bday}</span>
                                        <span>${name}</span>
                                    </li>`;
                            $("#finals-nomination-" + nomination.award + "-list").append($(li));
                            finalNominations[randInt] = nomination.id;
                            done += 1;
                            if (done == total) {
                                $(".finals-category-div").show();
                                $(".finals-please-wait").hide();
                            } else {
                                $(".finals-percent").text(`${done}/${total} sótt (${Math.floor(100 * done / total)}%)`);
                            }
                        }
                        if (judge_id) {
                            let j = _judges[judge_id];
                            name = j.name;
                            addNom();
                        } else {
                            name = "<i>Dómaralaust</i>";
                            addNom();
                        }
                       
                    }, null, [cat]);
                }
            }, null, [ENV.show]);
            break;
        }
        default: break;
    }
}

//ABS HANDLERS
function absAddToList(cat_id, entry_nr, judge_nr) {
    window.Api.get("cat", {}, function (msg) {
        if (msg.success) {
            let cat = msg.results;
            let l = $(`<li data-catalog = ${entry_nr}><b>${entry_nr}</b> - ${cat.name}</li>`);
            let x = $("#abs-list-judge-" + judge_nr);
            let inserted = false;
            for (let k of $(x).children()) {
                if ($(k).data("catalog") == entry_nr) {
                    inserted = true;
                    break;
                }
                if ($(k).data("catalog") > entry_nr) {
                    $(l).insertBefore(k);
                    inserted = true;
                    break;
                }
            }
            if (!inserted) {
                $(x).append(l);
            }
        } else {
            alert("2nd° error");
        }
    }, null, [cat_id]);
}
function abs_press_button_handler(e) {
    let integers = $("#textarea-abs").val().split(",");
    for (let int of integers) {
        let number = parseInt(int);
        if (int) {
            d = { "was_absent": true };
            window.Api.edit("entry", d, function (msg) {
                //We've recieved a response, If it worked, add to list. 
                if (msg.results.was_absent) {
                    let cat = msg.results;
                    let c = cat.cat;
                    let e = cat.catalog_number;
                    let j = cat.judge;
                    absAddToList(c, e, j);
                } else {
                    alert(cat.catalog_number + " could not be added to abs list");
                }
            },null, [ENV.show, int])
        }
        $("#textarea-abs").val("");
    }
}
function abs_remove_entry_handler(e) {
    let t = $(this).text()
    let me = this;
    if (window.confirm("Viltu fjarlægja " + t + " af ABS listanum?")) {
        let e = $(this).data("catalog");
        d = { "was_absent": false }
        window.Api.edit("entry", d, function (msg) {
            if (msg.success) {
                if (!msg.results.was_absent) {
                    $(me).remove();

                } else {
                    console.log(msg.results.was_absent)
                    alert("Ekki tókst að fjarlægja kött")
                }
            } else {
                alert(msg.error);
            }
        }, null, [ENV.show, e]);
    }
}

//COLOR HANDLERS
function colorGetEntrant(e) {
    e = parseInt($(this).val());
    if (e) {
        $("#color-change-form").hide();
        $("#color-warning").show();
        window.Api.get("entry", {}, function (msg) {
            let c = msg.results.cat;
            window.ENV.color_cat = c;
            window.Api.get("cat", {}, function (msg) {
                let cat = msg.results;
                let ems = cat.ems.split(" ");
                let breed = ems[0];
                let color = ems.slice(1).join(" ");
                $("#color-old-breed").val(breed);
                $("#color-old-color").val(color);
                $("#color-new-breed").val("");
                $("#color-new-color").val("");
                $("#color-new-breed").attr("placeholder", breed);
                $("#color-new-color").attr("placeholder", color);
                $("#color-change-form").show();
                $("#color-warning").hide();
                $("#color-change-name").text(`${cat.name} (#${e})`)
            }, [c]);
        }, null, [ENV.show, e]);
    }
}
function colorSaveEntrant(e) {
    let breed = $("#color-new-breed").val();
    let color = $("#color-new-color").val();
    if (breed == "") {
        breed = $("#color-old-breed").val();
    }
    if (color == "") {
        color = $("#color-old-color").val();
    }
    ems = breed + " " + color;
    d = {
        "ems": ems
    };
    window.Api.get("ems", d, function (msg) {
        if (msg.results.length == 0) {
            d2 = {
                "breed": breed
            };
            window.Api.get("ems", d2, function (msg) {
                if (msg.results.length == 0) {
                    warning("color", "'" + breed + "' er ekki löggild tegund");
                } else {
                    if (confirm("'" + color + "' er óþekktur litur fyrir tegund '" + breed + "'. Viltu skapa litinn núna?")) {
                        window.Api.create("ems", d, function (msg) {
                            colorSaveEntrant(e);
                        });
                    }
                }
            })

        } else {
            window.Api.edit("cat", d, function (msg) {
                $("#color-new-breed").val("");
                $("#color-new-color").val("");
                $("#color-old-breed").val("");
                $("#color-old-color").val("");
                warning("color", "");
                $("#color-change-form").hide();
                success("color", "Litadómur staðfestur. " + msg.results.name + " er nú " + msg.results.ems);
            }, null, [ENV.color_cat]);
        }
    });
}

//JUDGEMENT HANDLERS
function judgementGetEntrant(e) {
    ent = parseInt($(this).val());
    if (ent) {
        window.Api.get("entry", {}, function (entrant) {
            let biv, cert, abs, judgement, comment;
            entrant = entrant.results;
            ENV.entry = entrant.catalog_number;
            let judge = entrant.judge;
            let current_cert = entrant.current_certification;
            let next_cert = entrant.next_certification;
            let judgement_recieved = entrant.judgement_ready;
            let _class = entrant.class;
            let guest = entrant.is_guest;
            if (judgement_recieved && !guest) {
                biv = entrant.is_biv;
                cert = entrant.recieved_certification;
                abs = entrant.was_absent;
                judgement = entrant.judgement;
                comment = entrant.judgement_comment;
            } else {
                biv = false;
                cert = false;
                abs = false;
                judgement = "";
                comment = "";
            }

            console.log(judgement)
            window.Api.get("cat", {}, function (cat) {
                let ems = cat.results.ems;
                if (!guest && next_cert) {
                    window.Api.get("cert", {}, function (certificate) {
                        certificate = certificate.results;
                        let next_title;
                        if (certificate.ultimate) {
                            next_title = certificate.title_group;
                        } else {
                            next_title = " Enginn Titill ";
                        }

                        judgement_lockout(abs);
                        $("#judgement-form-cert").data("locked", false);
                        $("#judgement-form-biv").data("locked", false);
                        $("#judgement-form-biv").prop('disabled', false);
                        $("#judgement-form-abs").data("locked", false);
                        $("#judgement-form-abs").prop('disabled', false);
                        $("#judgement-form-cert").prop('disabled', false);

                        $("#judgement-form-ems").val(ems);
                        $("#judgement-form-judge").val(judge);
                        $("#judgement-form-class").val(_class);
                        $("#judgement-form-current-cert").val(current_cert);
                        $("#judgement-form-next-cert").val(next_cert);
                        $("#judgement-form-next-title").val(next_title);
                        console.log(judgement);
                        $("#judgement-form-judgement-given").val(judgement);
                        $("#judgement-form-biv").prop('checked', biv);
                        $("#judgement-form-abs").prop('checked', abs);
                        $("#judgement-form-cert").prop('checked', cert);
                        $("#judgement-form-comment").val(comment);
                    }, null, [next_cert]);
                } else {
                    $("#judgement-form-cert").data("locked", true);
                    $("#judgement-form-cert").prop('disabled', true);
                    if (guest) {
                        $("#judgement-form-abs").data("locked", true);
                        $("#judgement-form-biv").data("locked", true);
                        $("#judgement-form-biv").prop('disabled', true);
                        $("#judgement-form-abs").prop('disabled', true);
                        abs = true;
                    }
                    judgement_lockout(abs);
                    $("#judgement-form-ems").val(ems);
                    $("#judgement-form-judge").val(judge);
                    $("#judgement-form-class").val(_class);
                    $("#judgement-form-current-cert").val(current_cert);
                    $("#judgement-form-next-cert").val(next_cert);
                    $("#judgement-form-next-title").val("Enginn Titill");
                    $("#judgement-form-judgement-given").val(judgement);
                    $("#judgement-form-biv").prop('checked', biv);
                    $("#judgement-form-abs").prop('checked', abs);
                    $("#judgement-form-cert").prop('checked', cert);
                    $("#judgement-form-comment").val(comment);
                }
            },null, [entrant.cat]);
        }, null, [ENV.show, ent]);
    }
}
function judgement_lockout(locked) {
    if (locked) {
        $("#judgement-form-cert").data('old', $("#judgement-form-cert").prop("checked"));
        $("#judgement-form-biv").data('old', $("#judgement-form-biv").prop("checked"));
        $("#judgement-form-judgement-given").data("old", $("#judgement-form-judgemen-given").val());

        $("#judgement-form-judgement-given").val("");
        $("#judgement-form-cert").prop('checked', false);
        $("#judgement-form-biv").prop('checked', false);

        $("#judgement-form-biv").prop('disabled', true);
        $("#judgement-form-cert").prop('disabled', true);
        $("#judgement-form-judgement-given").prop('readonly', true);
        $("#judgement-form-judgement-given").addClass('readonly');
    } else {
        let cert = $("#judgement-form-cert").data('old');
        let biv = $("#judgement-form-biv").data('old', );
        let judgement = $("#judgement-form-judgement-given").data("old");

        $("#judgement-form-judgement-given").val(judgement);
        $("#judgement-form-cert").prop('checked', cert);
        $("#judgement-form-biv").prop('checked', biv);
        if ($("#judgement-form-cert").data('locked')) {

        } else {
            $("#judgement-form-biv").prop('disabled', false);
            $("#judgement-form-cert").prop('disabled', false);
        }
        $("#judgement-form-judgement-given").prop('readonly', false);
        $("#judgement-form-judgement-given").removeClass('readonly');
    }
}
function judgement_save() {
    let judge, judgement, biv, cert, abs, comment, entry;
    judge = $("#judgement-form-judge").val();
    judgement = $("#judgement-form-judgement-given").val();
    comment = $("#judgement-form-comment").val();
    biv = $("#judgement-form-biv").prop('checked');
    abs = $("#judgement-form-abs").prop('checked');
    cert = $("#judgement-form-cert").prop('checked');
    let d;
    d = {
        "is_biv": biv,
        "was_absent": abs,
        "recieved_certification": cert,
        "judgement": judgement,
        "judgement_comment": comment,
        "judge": judge
    }
    let entrant
    window.Api.edit("entry", d, function (entrant) {
        entrant = entrant.results;
        if (entrant.recieved_title) {
            alert("Titill veittur " + $("#judgement-form-next-title").val());
        } 
        judgement_clear();
        
    }, null, [ENV.show, ENV.entry]);
}
function judgement_clear() {
    $("#judgement-form .textinput").val("");
    $("#judgement-form input[type='checkbox']").prop("checked", false);
    judgement_lockout(false);
}

let nomJudge = null;
let nomFields = {};
let oldValues = {};
//Nominations handlers
function nomination_change_category(e) {
    let cat = $(this).val();
    $(".nomination-category-wrapper").hide();
    $(`.nomination-category-wrapper[data-category = "${cat}"]`).show();
}
function nomination_change_judge(e) {
    let jid = parseInt($("#nomination-form-judge").val());
    if (!jid) {
        jid = null;
    } 
    $(".nomination-field").val("");
    nomJudge = jid;
    nomFields = {};
    oldValues = {};
    d = {
        "judge": jid
    }
    window.Api.getAll("nomination", d, function (nominations) {
        nominations = nominations.results;
        for (let nom of nominations) {
            $(`#nomination_input_${nom.award}`).val(nom.entry);
            nomFields[nom.award] = nom.id;
            oldValues[nom.award] = nom.entry;
        }
    }, null, [ENV.show]);
}
function nomination_save_field(e) {

    $("#nomination-confirm").hide();
    let val = $(this).val()
    let award = $(this).data("value");
    let old = oldValues[award];
    let uri = nomFields[award];
    let t = this;
    console.log(val + " = " + uri);
    if (val === "" && uri && uri !== "") {
        console.log(9)
        window.Api.delete("nomination", {}, function (empty) {
            oldValues[award] = "";
            nomFields[award] = "";
            $("#nomination-confirm").hide();
        }, null, [ENV.show, uri]);
        return;
    } else if (val === "") {
        return;
    }
    window.Api.get("entry", d, function (entry) {
        entry = entry.results;
        if (nomJudge && nomJudge != entry.judge) {
            if (!confirm("Köttur " + entry.catalog_number + " er ekki í dóm hjá dómara. Ertu viss um tilnefninguna?")) {
                $(t).val(old);
                return;
            }
        }
        if (uri) {
            d = {
                "entry": val
            }
            window.Api.edit("nomination", d, function (entry) {
                oldValues[award] = val;
                $("#nomination-confirm").show();
            }, [ENV.show, uri])
        } else {
            d = {
                "entry": val,
                "judge": nomJudge,
                "award": award,
                "bis": false,
            }
            window.Api.create("nomination", d, function (nomination) {
                nomination = nomination.results;
                oldValues[award] = val;
                nomFields[award] = nomination.uri;
                $("#nomination-confirm").show();
            }, null, [ENV.show])
        }
    }, null,[ENV.show, val]);

}

// Finals
let finalNominations = {};
let finalasyncRequests = {}

function finals_change_category(e) {
    let cat = $(this).val();
    $(".finals-category-wrapper").hide();
    $(`.finals-category-wrapper[data-category = "${cat}"]`).show();
}
function finals_toggle_bis(e) {
        let id = $(this).data("id");
        let uri = finalNominations[id];
        let selected = $(this).prop("checked");
        d = {
            "bis": selected
        }
        window.Api.edit("nomination", d, null, null [ENV.show, uri]);
}

file = null;
fileName = null;
//Files
function files_get_file(e) {
    if (!file) {
        return;
    }
    settings = {}
    for (let checkbox of $(".files_settings_checkbox")) {
        let section = $(checkbox).parents(".files_checkbox_wrapper").data("setting");
        if (!settings[section]) {
            settings[section] = [];
        }
        if (!$(checkbox).prop("checked")) {
            continue;
        }
        let val = $(checkbox).val()
        settings[section].push(val);
    }
    let el = $("#files_settings_catorder li");
    let ox = []
    for (let ll of el) {
        ox.push($(ll).data("value"));
    }
    settings["category_order"] = ox

    d = {
        "filters":settings
    }

    p = JSON.stringify(d)
    newFile = file+ "?data="+p
    getFile(newFile, {}, fileName);
}

///MISC

function warning(section, warning) {
    $("#warning-" + section).text(warning);
}
function success(section, text) {
    $("#success-" + section).text(text);
}
function getAgeString(older, newer) {
    old = new Date(older);
    young = new Date(newer);
    months =  young.getMonth() - old.getMonth();
    years = young.getYear() - old.getYear();
    while (months < 0) {
        months += 12;
        years -= 1;
    }
    
    return (years > 0) ? years + "y " + months + "m" : months + "m" ;
}
function getFile(url, getData, filename) {
    var xhr = new XMLHttpRequest();
    xhr.open("GET", url);
    xhr.responseType = "blob";

    xhr.onload = function () {
        saveData(this.response, filename); 
    };
    xhr.send(getData);
}
function saveData(blob, fileName) // does the same as FileSaver.js
{
    var a = document.createElement("a");
    document.body.appendChild(a);
    a.style = "display: none";

    var url = window.URL.createObjectURL(blob);
    a.href = url;
    a.download = fileName;
    a.click();
    window.URL.revokeObjectURL(url);
}
})();