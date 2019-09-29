$(document).ready(function (e) {
	let show_id;
	let not_included = [];
	let included = [];
    $("#showAward-avaliable-awards li").on("click touchstart", function(e){
		let id = $(this).data("value")
		let me = $(this).detatch();
		$(me).attachTo("#showAward-included-awards");
		let index = not_included.indexOf(id);
		not_included.splice(index,1);
		included.push(id);
		
	});
	
	$("#showAward-included-awards li").on("click touchstart", function(e){
		let id = $(this).data("value")
		let me = $(this).detatch();
		$(me).attachTo("#showAward-this-awards");
		let index = included.indexOf(id);
		included.splice(index,1);
		not_included.push(id);
	});

    window.ModuleManager.registerModuleHandler("showAward", "activate", function () {
		let msg = window.ModuleManager.getMessage("showAward");
        if (msg) {
			show_id = msg;
        }
		//Fetch the show
		window.Api.get("show",{},function(show){
			//what awards are included?
			let show = show.results;
			let offered_awards = show.awards_offered;
			//Fetch the global awards
			window.Api.get("award",{},function(awards){
				awards = awards.results;
				$("#showAward-avaliable-awards").empty();
				$("#showAward-included-awards").empty();
				//Append each award to the correct window. 
				for(let award of awards){
					let li = `<li data-value = ${award.id} class="list-window-element"> ${award.name}</li>`;
					if(offered_awards.includes(award.id)){
						$("#showAward-included-awards").append(li);
						included.push(award.id);
					} else{
						$("#showAward-avaliable-awards").append(li);
						not_included.push(award.id);
					}
				}
			});
		},[show_id]);

    })

    window.ModuleManager.registerModuleHandler("showAward", "save", function () {
		let d = {
			"awards_offered": included
		};
		window.Api.edit("show",d,function(msg){
			 window.ModuleManager.saveSuccess("showAward", msg.results, msg.results);
		},[show_id]);
    })

    window.ModuleManager.activateModule("showAward");  

});


