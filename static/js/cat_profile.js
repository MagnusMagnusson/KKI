$("document").ready(function (e) {
    document.addEventListener("module-success", function (e) {
        let data = e.detail;
        console.log("HEARD");
        if (data.module = "catNeuter") {
            console.log(data);
            let text = $("#neuterText").text();
            newText = (text == "Ógeld") ? "Geld" : "Geldur";
            $("#neuterText").text(newText);
        }
    });
})