$(document).ready(function () {
    $("#sidebar-list a").on("click touchstart", function (e) {
        $(".main-section").hide();
        newSection = $(this).data("section")
        $("#section-" + newSection).show();
        updateData(newSection);
    });

    $(document).on("click touchstart", ".judge-abs-list li", abs_remove_entry_handler);

    $(document).on("click touchstart", "#button-confirm-abs", abs_press_button_handler);
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