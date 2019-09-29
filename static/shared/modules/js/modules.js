$(document).ready(function (e) {
    $(document).on('click', ".button.section", function (e) {
        e.stopPropagation();
        let myModule = $(this).parents(".module")[0];
        console.log(myModule);
        $(myModule).find(".button.section.selected").removeClass("selected");
        $(this).addClass("selected");
        var d = $(this).data("section");
        $(myModule).find("section").hide();
        $(myModule).find("section[data-section='" + d + "']").show();
    });

    $(document).on('click', ".module-close", function (e) {
        let myName = $(this).parents(".module").data("module");
        window.ModuleManager.closeModule(myName);
    });

    $(document).on('click', ".module-save", function (e) {
        let myName = $(this).parents(".module").data("module");
        window.ModuleManager.saveModule(myName);
    });

    $(".module.popup").show();
    

});

