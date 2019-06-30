$(document).ready(function (e) {
    $(document).on('click', ".button.section", function (e) {
        e.stopPropagation();
        $(".button.section.selected").removeClass("selected");
        $(this).addClass("selected");
        var d = $(this).data("section");
        $(".module.popup section").hide();
        $(".module.popup section[data-section='" + d + "']").show();
    });

    $(document).on('click', ".module-close", function (e) {
        let myName = $(this).parents(".module").data("module");
        window.ModuleManager.closeModule(myName);
    });

    $(".form-kt").each(function () {
        new Cleave(this, {
            delimiter: '-',
            blocks: [6, 4]
        });
    })
    
});
