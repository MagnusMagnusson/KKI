$(document).ready(function () {
    $(".textinput").val("");
    $("input").prop("checked", false);

    $("#judgement-form-abs").change(function () {
        if (this.checked) {
            judgement_lockout(true);
        } else {
            judgement_lockout(false);
        }
    });

    $("#sidebar-list a").on("click touchstart", function (e) {
        $(".main-section").hide();
        newSection = $(this).data("section")
        $("#section-" + newSection).show();
        updateData(newSection);
    });

    $(document).on("click touchstart", ".judge-abs-list li", abs_remove_entry_handler);

    $(document).on("click touchstart", "#button-confirm-abs", abs_press_button_handler);
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
});

function updateData(section) {
    switch (section) {
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
            }, [ENV.show]);
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
    }, [cat_id]);
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
            }, [ENV.show, int])
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
        }, [ENV.show, e]);
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
        }, [ENV.show, e]);
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
                    if (confirm("'" + color + "' er óþekktur litur fyrir tegund '"+breed+"'. Viltu skapa litinn núna?")) {
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
                success("color", "Litadómur staðfestur. "+msg.results.name + " er nú " + msg.results.ems);
            }, [ENV.color_cat]);
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
                if (!guest && next_cert){
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
                    }, [next_cert]);
                } else {
                    $("#judgement-form-cert").data("locked", true);
                    $("#judgement-form-cert").prop('disabled', true);
                    if (is_guest) {
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
            }, [entrant.cat]);
        }, [ENV.show, ent]);
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
        "judge":judge
    }
    window.Api.edit("entry", d, function (entrant) {
        let entrant = entrant.results;
        if (entrant.recieved_title) {
            $("#judgement-form-next-title").addClass("glow-green");
        } else {
            judgement_clear();
        }
    }, [ENV.show, ENV.entry]);
}
function judgement_clear() {

}


function warning(section,warning) {
    $("#warning-" + section).text(warning);
}
function success(section, text) {
    $("#success-" + section).text(text);
}