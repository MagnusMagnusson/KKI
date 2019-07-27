//Profile.js
//Shared .js file for all profiles. 

$(document).ready(function (e) {
    //Show the first profile section, and dynamically create their buttons. 
    $($("#profile-sections section")[0]).show();

    //button creation
    s = $("#profile-sections section");
    var first = true;
    for (let x of s) {
        let title = $(x).data("name");
        let button = $(`<span data-section="title" class="section-button">${title}</span>`);
        $("#profile-sections-buttons").append(button);
        if (first) {
            first = false;
            $(button).addClass("selected");
        }
        //Clicking the button highlightsit, unselectes previous button, and shows relevant slide. 
        $(button).on("click touchstart", function (e) {
            e.preventDefault();
            let friend = $(`#profile-sections section[data-name='${title}']`);

            $(".section-button.selected").removeClass("selected");
            $(button).addClass("selected");
            $("#profile-sections section").hide();
            $(friend).show();

        });
    }
})