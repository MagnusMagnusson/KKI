$(document).ready(function () {
    window.Api = new Api();
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

