$(document).ready(function () {
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


function warning(section,warning) {
    $("#warning-" + section).text(warning);
}
function success(section, text) {
    $("#success-" + section).text(text);
}