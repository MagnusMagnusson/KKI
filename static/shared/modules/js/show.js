$(document).ready(function (e) {

    $(document).on('input',"#show-organizer-name", function (e) {
        e.stopPropagation();
        let text = $("#show-organizer-name").val();
        if (text.length < 3) {
            $("#show-organizer-name-wrapper .result-box").hide();
            return;
        }
        window.Api.find({ 'type': 'member', 'term': 'name', 'value': text }, function (e) {
            let list = $("#show-organizer-name-wrapper .result-box .result-box-list");
            $(list).empty();
            i = 0;
            for (let x of e.results.slice(0,10)) {
                let li = $(`<li>${x[1].name}</li>`)
                $(list).append(li);

                $(li).on("click touchstart", function (e) {
                    e.preventDefault();
                    $("#show-oragnizer-mid").val(x[1].id);
                    $("#show-organizer-name").val(x[1].name);
                    $("#show-organizer-ssn").val(x[1].ssn);
                    $("#show-organizer-name-wrapper .result-box").hide();
                });
            }
            $("#show-organizer-name-wrapper .result-box").show();

        });
    });

    window.ModuleManager.registerModuleHandler("show", "activate", function () {
        $('[name="date"]').val(new Date().toISOString().split('T')[0]);
    })

    window.ModuleManager.registerModuleHandler("show", "save", function () {
        let a = $("#show-form").serializeArray();
        let d = {}
        for (let x of a) {
            d[x.name] = x.value;
        }

        string = JSON.stringify(d);
        d = {};
        d['data'] = string;
        console.log(d);
        window.Api.submitShow(d, function (msg) {
            window.ModuleManager.saveSuccess("show",msg,msg);
        });
    })

    window.ModuleManager.activateModule("show");  

    $("#show-organizer-ssn").each(function () {
        new Cleave(this, {
            delimiter: '-',
            blocks: [6, 4]
        });
    })
});


