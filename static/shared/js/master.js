ENV = {};
$(document).ready(function () {
    window.Api = new Api();
    window.Util = new Util();
    window.ModuleManager = new ModuleManager();
    var csrftoken = jQuery("[name=csrfmiddlewaretoken]").val();
    function csrfSafeMethod(method) {
        // these HTTP methods do not require CSRF protection
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }
    $.ajaxSetup({
        beforeSend: function (xhr, settings) {
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });

    $(document).on("click touchstart", function (e) {
        var container = $(".result-box");

        // if the target of the click isn't the container nor a descendant of the container
        if (!container.is(e.target) && container.has(e.target).length === 0) {
            container.hide();
        }

        var container = $("#navbar-settings-div");
        var gearButton = $("#navbar_setting_button");

        // if the target of the click isn't the container nor a descendant of the container
        if (!gearButton.is(e.target) && !container.is(e.target) && container.has(e.target).length === 0) {
            container.hide();
        }
    });

    $("#navbar_settings_button_logout").on("click touchstart", function (e) {
        $.ajax({
            type: "POST",
            url: "/api/logout",
            dataType: 'json',
            success: function (d) {
                if (d.success) {
                    window.location = "/";
                }
            }
        });
    })

    $("#navbar_setting_button").on("click touchstart", function (e) {
        $("#navbar-settings-div").show();
    });

    var notLocked = true;
    $.fn.animateHighlight = function (highlightColor, duration) {
        var highlightBg = highlightColor || "#FFFF9C";
        var animateMs = duration || 1500;
        var originalBg = this.css("color");
        console.log(originalBg);
        
        if (notLocked) {
            notLocked = false;
            this.stop().css("color", highlightBg)
                .animate({ color: originalBg }, animateMs);
            setTimeout(function () { notLocked = true; }, animateMs);
        }
    };
});


Math.clamp = function (value, min, max) {
    return Math.min(max, Math.max(min, value));
}

function progressBar_create(element, steps){
    let progressColors = `<b>Skref <i class='progress-steps'>1/${steps}</i></b>
    <div class="fulldiv"></div>
    <div class="progress-color graydiv"></div>
    <div class="progress-color orangediv"></div>`;
    $(element).append(progressColors);
    let el = { element, steps, "current": 0 };
    progressBar_increment(el, 0);
    return el;
}


function progressBar_increment(barDict, incrementSize) {
    let totalSize = barDict.steps;
    let newSize = Math.clamp(barDict.current + incrementSize, 0, totalSize);
    barDict.current = newSize;
    let completeStep = (100 / totalSize) * newSize;
    let nextStep = Math.clamp(completeStep + (100 / totalSize), 0, 100);

    let stepText = (newSize === totalSize) ? (newSize) + "/" + totalSize : (1 + newSize) + "/" + totalSize;

    $(barDict.element).find(".graydiv").css("width", (nextStep) + "%");
    $(barDict.element).find(".orangediv").css("width", (completeStep) + "%");
    $(barDict.element).find(".progress-steps").text(stepText);
}
