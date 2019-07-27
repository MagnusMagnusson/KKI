/* Cat_profile.js
    .js file governing the dynamic behaviours of the cat profiles
*/

$("document").ready(function (e) {
    //Module event listeners. 
    document.addEventListener("module-success", function (e) {
        let data = e.detail;

        switch (data.module) {
                //If the CatNeuter module reports a success, change the text from "unneutered" to "neutered"
            case "catNeuter": {
                let text = $("#neuterText").text();
                newText = (text == "Ógeld") ? "Geld" : "Geldur";
                $("#neuterText").text(newText);
                break;
            }
                //If the CatOwner module reports a success, update the current owner list
                // TODO: Update the owner history tab. 
            case "catOwner": {
                $("#owner-list").empty();
                for (o of data.result.owners) {
                    console.log(o);
                    let name = o.person.name;
                    let date = o.date;
                    let address = o.person.address + ", " + o.person.city + ", (" + o.person.postcode + ")";
                    let phone = "";
                    if (o.person.phone && o.person.phone !== "") {
                        phone = o.person.phone + ", " ;
                    } 
                    let email = o.person.email;

                    let li = $(`<li>
                        E. ${name} síðan ${date} </br>
                        <small>${address}. ${phone} ${email} </small>
                        </li>
                    `);
                    console.log(li);
                    $("#owner-list").append(li);
                }
                break;
            }
        }
    });
})