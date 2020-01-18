/* show_management.js
    .js file governing the dynamic behaviours of the show profile
*/

$("document").ready(function (e) {
    //Module event listeners. 
    document.addEventListener("module-success", function (e) {
        let data = e.detail;
        switch (data.module) {
            case "showJudge": {
                //Empty the show judges list, and repopulate with the data provided. 
                $("#judges-overview-list").empty();
                for (let judge of data.result.judges) {
                    //Fetch the name and country of all the judges in question
                    window.Api.get("judge", {}, function (person) {
                        person = person.results;
                        let li = `<li>${person.name} [${person.country}]</li>`
                        $("#judges-overview-list").append(li);
                    }, null,s [judge]);
                }
            }
            break;
        }
    });
})