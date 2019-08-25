/* show_master.js
    .js file governing the dynamic behaviours of the show sidebar
*/

$("document").ready(function (e) {
    //Module event listeners. 
    document.addEventListener("module-success", function (e) {
        let data = e.detail;
        switch (data.module) {

            case "show": {
                if (data.result) {
                    window.location = "/syningar/" + data.result.result.id + "/setup";
                }
                break;
            }
        }
    });
})