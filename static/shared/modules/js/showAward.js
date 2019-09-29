$(document).ready(function (e) {
	let show_id;
	let not_included = [];
	let included = [];
    $(document).on("click", "#showAward-avaliable-awards li", function (e) {
        let id = $(this).data("value")
        let me = $(this).detach();
		$(me).appendTo("#showAward-included-awards");
		let index = not_included.indexOf(id);
        not_included.splice(index, 1);
        console.log(not_included);
		included.push(id);
		
	});
	
    $(document).on("click", "#showAward-included-awards li", function (e) {
		let id = $(this).data("value")
        let me = $(this).detach();
		$(me).appendTo("#showAward-avaliable-awards");
		let index = included.indexOf(id);
        included.splice(index, 1);
        console.log("included");
        console.log(included);
		not_included.push(id);
    });

    $(document).on("click", "#showAward-form-newAward-save", function (e) {
        let name = $("#showAward-form-newAward-name").val();
        let optional = $("#showAward-form-newAward-core").prop("checked");
        d = {
            "name": name,
            "is_core": !optional
        }
        window.Api.create("award", d, function (msg) {
            msg = msg.results;
            included.push(msg.id);
            let li = `<li data-value = ${msg.id} class="list-window-element"> ${msg.name}</li>`;
            $("#showAward-included-awards").append(li);
            $("#showAward-form-newAward-name").val("");
            let optional = $("#showAward-form-newAward-core").prop("checked", false);
            $("#showAward-basic-section").click();
        })
    });

    window.ModuleManager.registerModuleHandler("showAward", "activate", function () {
		let msg = window.ModuleManager.getMessage("showAward");
        if (msg) {
			show_id = msg;
        }

        $("#showAward-avaliable-awards").empty();
        $("#showAward-included-awards").empty();
		//Fetch the show
		window.Api.get("show",{},function(show){
			//what awards are included?
			show = show.results;
			let offered_awards = show.awards_offered;
			//Fetch the global awards
            let getAwardPage = function (page) {
                console.log("page " + page);
                window.Api.get("award", {},function (awards) {
                    addAwardPage(awards.results, offered_awards);
                    page = 1 + awards.page;
                    total_pages = awards.total_pages;
                    if (page < total_pages) {
                        getAwardPage(page);
                    }
                }, [], page);
            }
            getAwardPage(0);           
		},[show_id]);

    })

    window.ModuleManager.registerModuleHandler("showAward", "save", function () {
        console.log(included);
		let d = {
			"awards_offered": included
		};
		window.Api.edit("show",d,function(msg){
			 window.ModuleManager.saveSuccess("showAward", msg.results, msg.results);
		},[show_id]);
    })

    window.ModuleManager.activateModule("showAward");  

    function addAwardPage(results, offered_awards) {
        //Append each award to the correct window. 
        for (let award of results) {
            let li = `<li data-value = ${award.id} class="list-window-element"> ${award.name}</li>`;
            if (offered_awards.includes(award.id)) {
                $("#showAward-included-awards").append(li);
                included.push(award.id);
            } else {
                $("#showAward-avaliable-awards").append(li);
                not_included.push(award.id);
            }
        }
    }
});


