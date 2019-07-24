$("document").ready(function (e) {
    document.addEventListener("module-success", function (e) {
        let data = e.detail;

        switch (data.module) {
            case "catNeuter": {
                let text = $("#neuterText").text();
                newText = (text == "Ógeld") ? "Geld" : "Geldur";
                $("#neuterText").text(newText);
                break;
            }
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