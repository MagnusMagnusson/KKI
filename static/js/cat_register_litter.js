$(document).ready(function (e) {
    let DEBUG = true;
    let form_data;
    form_data = {
        'cattery': null,
        'sire': null,
        'dam': null,
        'birthdate': null,
        'litterCount': null
    }
    let confirmationRequestId = null;
    let breedCache = [];
    let newOrgs = [];
    let newColors = [];
    let newOwners = [];
    let progressBar = progressBar_create(".progressbar", 6);

    let countryForm = false;

    function getKitten(i) {
        let formName = "#litter_kitten_" + i;
        formObject = $(formName).serializeArray();

        let cattery = form_data.cattery
        formObject.push({ 'name': 'cattery', 'value': cattery });
        let sire = form_data.sire;
        formObject.push({ 'name': 'sire', 'value': sire });
        let dam = form_data.dam;
        formObject.push({ 'name': 'dam', 'value': dam });
        let birthdate = form_data.birthdate;
        formObject.push({ 'name': 'birthdate', 'value': birthdate });
        let owner = {};
        owner.cat = i;
        let kitten = {};
        for (let field of formObject) {
            if (field.name === "owner") {
                owner.ssn = field.value;
                owner.id = owner.ssn;
            }
            if (field.name === "foreign_owner") {
                owner.isForeign = field.value === "on";
            }
            kitten[field.name] = field.value;
        }
        kitten.owner = owner;
        kitten.owner.isForeign = kitten.owner.isForeign || false;
        if (kitten.owner.isForeign) {
            kitten.owner.id = i;
        } else {
            if (kitten.owner.ssn.length !== 11) {
                kitten.owner.id = "CATTERY";
            }
        }
        return kitten;
    }

    function validate_postform() {
        if (DEBUG) {
            return true;
        }
        let lc = form_data.litterCount;
        for (let i = 1; i <= lc; i++) {
            let form_id = `#litter_kitten_${i}`;
            let stringValues = ['name', 'ems', 'microchip', 'country', 'organization'];
            //All values that are simple text entry.
            for (let n of stringValues) {
                let s = `${form_id} input[name = '${n}']`;
                let val = $(s).val();
                if (typeof val === "undefined" || val == "") {
                    console.log("string " + i + " - " + n + " - " + val);
                    return false;
                }
            }
            //gender
            let gend = $(`${form_id} input[name="gender"]:checked`).val();
            if (typeof gend === "undefined" || gend === null) {
                console.log("string " + i + " - gender - " + gend);
                return false;
            }
            //registration number. 
            let regnr = $(`${form_id} input[name="registry_digits"]`).val();
            if (regnr && regnr > 0) {
                //cont. Maybe add async validation here. 
            } else {
                console.log("string " + i + " - " + regnr);
                return false;
            }

            let kt = $(`${form_id} input[name="owner"]`).val();
            let ssn = kt.replace("-", "");
            if (kt.length !== 0 && !window.Util.ssn_valid(ssn)) {
                return false;
            }
        }
        return true;
    }

    function validate_preform() {
        if (DEBUG) {
            return true;
        }
        for (let key in form_data) {
            if (form_data[key] === null) {
                return false;
            }
        }
        return true;
    }

    function postform_errors_show() {
        $(".warning").hide();
        let lc = form_data.litterCount;
        for (let i = 1; i <= lc; i++) {
            let form_id = `#litter_kitten_${i}`;
            let stringValues = ['name', 'ems', 'microchip', 'country', 'organization'];
            let errorMatch = { 'name': 'w_nafn', 'ems': 'w_ems', 'microchip': 'w_micro', 'country': 'w_skrn', 'organization': 'w_skrn' };
            //All values that are simple text entry.
            for (let n of stringValues) {
                let s = `${form_id} input[name = '${n}']`;
                let val = $(s).val();
                if (typeof val === "undefined" || val == "") {
                    let error = errorMatch[n];
                    console.log(n);
                    $(`${form_id} .${error}`).show();
                }
            }
            //gender
            let gend = $(`${form_id} input[name="gender"]:checked`).val();
            if (typeof gend === "undefined" || gend === null) {
                $(`${form_id} .w_gender`).show();
            }
            //registration number. 
            let regnr = $(`${form_id} input[name="registry_digits"]`).val();
            if (regnr && regnr > 0) {
                //cont. 
            } else {
                $(`${form_id} .w_skrnr`).show();
            }

            let kt = $(`${form_id} input[name="owner"]`).val();

            let ssn = kt.replace("-", "");
            if (kt.length !== 0 && !window.Util.ssn_valid(ssn)) {
                $(`${form_id} .w_ssn`).show();
            }
        }
    }

    function preform_errors_show() {
        $(".warning").hide();
        if (form_data.cattery === null) {
            $("#lr_cattery_registry_id_wrapper .warning").show();
        }

        if (form_data.sire === null) {
            $("#lr_sire_registry_wrapper .warning").show();
        }

        if (form_data.dam === null) {
            $("#lr_dam_registry_wrapper .warning").show();
        }

        if (form_data.birthdate === null) {
            $("#lr_birthdate_wrapper .warning").show();
        }

        if (form_data.litterCount === null) {
            $("#lr_littersize_wrapper .warning").show();
        }
    }

    $("#lr_birthdate").on('input', function (e) {
        form_data.birthdate = $(this).val();
    });
    $("#lr_littercount").on('input', function (e) {
        if ($(this).val() > 0) {
            form_data.litterCount = $(this).val();
        } else {
            form_data.litterCount = null;
        }
    });

    //Search result population. 
    $("#lr_cattery_registry").on("input", function (e) {
        let text = $(this).val();
        if (text.length < 3) {
            return;
        }
        form_data.cattery = null;
        let d = {
            'name': text
        };

        window.Api.find("cattery", d, function (e) {
            if (e.results.length == 0) {
                return;
            }
            $("#lr_cattery_registry_results .result-box-list").empty();
            for (res of e.results.slice(0, 10)) {
                let cattery = res;
                li = $(`<li>${cattery.name}</li>`);
                $("#lr_cattery_registry_results .result-box-list").append(li);

                $(li).on("click touchstart", function (e) {
                    $("#lr_cattery_registry").val(cattery.name);
                    form_data.cattery = cattery.id;
                    $("#lr_cattery_registry_results").hide();
                });
            }
            $("#lr_cattery_registry_results").show();
        });
    });

    $(".parent-search").on("input", function (e) {
        let text = $(this).val();
        if (text.length < 3) {
            return;
        }

        let fill = $(this).data("fill");

        let s = {
            'registry_number': text
        };

        let f = {
            "gender": fill == "sire" ? "male" : "female",
            "neutered": false
        };

        window.Api.getfind("cat", f, s, function (e) {
            if (e.results.length == 0) {
                return;
            }
            $(`#lr_${fill}_registry_results .result-box-list`).empty();
            for (res of e.results.slice(0, 10)) {
                let cat = res;
                li = $(`<li>${cat.name}</li>`);
                $(`#lr_${fill}_registry_results .result-box-list`).append(li);

                $(li).on("click touchstart", function (e) {
                    form_data[fill] = cat.id;
                    $(`#lr_${fill}_registry`).val(cat.registry);
                    $(`#lr_${fill}_registry_name`).val(cat.full_name);
                    $(`#lr_${fill}_registry_ems`).val(cat.ems);
                    $(`#lr_${fill}_registry_micro`).val(cat.microchip);
                    $(`#lr_${fill}_registry_birthdate`).val(cat.birthdate);
                    $(`#lr_${fill}_registry_results`).hide();
                });
            }
            $(`#lr_${fill}_registry_results`).show();
        });
    });

    $("#lr_next_button").on("click touchstart", function (e) {
        e.preventDefault();
        let littersize = parseInt($("input[name='litter_amount']").val());
        if (validate_preform()) {
            for (let i = 0; i < littersize; i++) {
                let formHtml = getLitterKittenForm(1 + i);
                let formdiv = $(formHtml);
                $("#lr_kitten_formlist").append(formdiv);
                window.Api.getNextRegNr(function (e) {
                    let nr = i + e.result;
                    $(formdiv).find(`input[name='registry_digits`).val(nr);
                })
            }
            progressBar_increment(progressBar, 1);
            $("#lr_pairing").fadeOut({
                complete: function () {
                    $("#lr_kitten_section").fadeIn();
                    $("#lr_pairing").removeClass("activeSection");
                    $("#lr_kitten_section").addClass("activeSection");
                }
            });

            $("#lr_kitten_section .form_kt").each(function () {
                new Cleave(this, {
                    delimiter: '-',
                    blocks: [6, 4]
                });
            })
        } else {
            preform_errors_show();
        }
    });

    $("#confirm_new_people").on('click touchstart', function (e) {
        saveNewPeople();
    })

    window.getKitty = function (i) {
        let k = getKitten(i);

        string = JSON.stringify(k);
        console.log(string);
    }

    $("#confirm_litter_button").on("click touchstart", function (e) {
        let littersize = form_data.litterCount;
        let regDigits = [];
        let valid = true;
        $(".warning").hide();
        //See if the form is valid.
        if (!validate_postform()) {
            postform_errors_show();
            valid = false;
        }
        //Check if the digits of any of the kittens are the same.
        for (let i = 1; i <= littersize; i++) {
            kitten = getKitten(i);
            let digits = kitten.registry_digits;
            if (regDigits.indexOf(digits) >= 0) {
                valid = false;
                $(`#litter_kitten_${i} .w_skrn`).show();
            } else {
                regDigits.push(digits);
            }
        }
        if (!valid) { //Invalid. Abort. 
            return;
        } else { //All good so far. Start checking for global uniqueness and then head to confirmation. 
            validateUniqueKitten(littersize);
        }
    });

    function saveEntries() {

    }

    function confirmEntries() {

    }

    function saveNewStructures() {

    }

    function showNewStructures() {
        if (newOrgs.length > 0 || newOwners.length > 0) {
            if (!countryForm) {
                window.Util.forms_countrySelection(function (e) {
                    countryForm = e;
                    showNewStructures();
                });
                return;
            }
        }

        $("#lr_orgs_formlist").hide();
        $("#lr_colors_formlist").hide();
        $("#lr_ssn_formlist").hide();

        if (newColors.length > 0) {
            let colorForms = "";
            for (let i = 0; i < newColors.length; i++) {
                let ems = newColors[i].split(" ");
                let c, b;
                b = ems[0];
                c = ems.splice(1).join(" ");
                colorForms += "<div class='top-space'>";
                colorForms += getNewColorForm(i, b, c);
                colorForms += "</div>";
            }
            $("#lr_colors_formlist").empty();
            $("#lr_colors_formlist").append($(colorForms));
            $("#lr_colors_formlist").show();
        }

        if (newOwners.length > 0) {
            let peopleForms = "";
            for (let i = 0; i < newOwners.length; i++) {
                let ssn = newOwners[i];
                peopleForms += "<div class='top-space'>";
                peopleForms += getNewPersonForm(i, ssn);
                peopleForms += "</div>";
            }
            $("#lr_ssn_formlist").empty();
            $("#lr_ssn_formlist").append($(peopleForms));
            $("#lr_ssn_formlist").show();
        }

        if (newOrgs.length > 0) {
            let orgForm = "";
            for (let i = 0; i < newOrgs.length; i++) {
                let acronym = newOrgs[i];
                orgForm += "<div class='top-space'>";
                orgForm += getNewOrginazationForm(i, acronym);
                orgForm += "</div>";
            }
            $("#lr_orgs_formlist").empty();
            $("#lr_orgs_formlist").append($(orgForm));
            $("#lr_orgs_formlist").show();
        }
        $("#lr_kitten_section").fadeOut({
            complete: function () {
                $("#lr_kitten_new_data").fadeIn();
            }
        });

    }

    function validateNewStructures() {
        console.log("ValidateNewStructures");
        confirmationRequestId = Math.floor(Math.random() * Math.pow(2, 32));
        getNewPeople();
    }

    function getNewPeople() {
        console.log("hello!");
        let confirmationRequestsWaiting;
        let currentId = confirmationRequestId;
        let owners = [];
        newOwners = [];

        for (let i = 1; i <= form_data.litterCount; i++) {
            let k = getKitten(i);
            console.log(k.owner);
            let owner = k.owner;
            owner.ssn = owner.ssn.replace("-", "");
            if (owners.map(x => x.id).indexOf(owner.id) === -1) {
                console.log(owner.ssn);
                if (owner.ssn.length === 10 || owner.isForeign) {
                    console.log("valid");
                    if (window.Util.ssn_valid(owner.ssn) || owner.isForeign) {
                        owners.push(owner);
                    }
                }
            }
        }
        console.log(owners);
        confirmationRequestsWaiting = owners.length;
        if (confirmationRequestsWaiting === 0) {
            progressBar_increment(progressBar, 1);
            getNewColors();
        } else {
            for (let owner of owners) {
                if (owner.isForeign) {
                    confirmationRequestsWaiting--;
                    newOwners.push(owner);
                    if (confirmationRequestsWaiting === 0) {
                        progressBar_increment(progressBar, 1);
                        showNewPeople();
                    }
                }
                d = { "ssn": owner.ssn }
                window.Api.get("person", d, function (e) {
                    if (currentId === confirmationRequestId) {
                        if (e.count === 0) {
                            newOwners.push(owner);
                        }
                        confirmationRequestsWaiting--;
                        if (confirmationRequestsWaiting === 0) {
                            progressBar_increment(progressBar, 1);
                            showNewPeople();
                        }
                    }
                }, []);
            }
        }
    }

    function showNewPeople() {
        console.log("showNewPeople()");

        if (!countryForm) {
            window.Util.forms_countrySelection(function (e) {
                countryForm = e;
                showNewPeople();
            });
            return;
        }
        console.log(newOwners);
        $("#lr_ssn_formlist").hide();

        let peopleForms = "";
        for (let i = 0; i < newOwners.length; i++) {
            let o = newOwners[i];
            let ssn = o.isForeign ? "Á ekki við" : o.ssn.substr(0, 6) + "-" + o.ssn.substr(6, 4);;
            let cat = getKitten(o.cat).name;
            peopleForms += "<div class='top-space'>";
            peopleForms += `<b>Skráðu eiganda '${cat}'</b>`;
            peopleForms += getNewPersonForm(i, ssn);
            peopleForms += "</div>";
            newOwners[i].form = "#person-form-" + i;
        }
        $("#lr_ssn_formlist").empty();
        $("#lr_ssn_formlist").append($(peopleForms));
        $("#lr_ssn_formlist").show();
        $(".activeSection").fadeOut({
            complete: function () {
                $("#lr_kitten_new_owners").fadeIn();
                $(".activeSection").removeClass("activeSection");
                $("#lr_kitten_new_owners").addClass("activeSection");
            }
        });
    }

    function saveNewPeople() {
        let newPeople = [];
        let jsonMap = [];
        for (let o of newOwners) {
            let person = $(o.form).serializeArray();
            let personJson = JSON.stringify(person);
            if (jsonMap.indexOf(personJson) === -1) {
                jsonMap.push(personJson);
                map[personJson] = o;
                newPeople.push(person);
                o.requestDict = person;
            }
        }
        for (let pp of newPeople) {
            window.Api.create("person", pp, function (msg) {
                let Js = JSON.stringify(pp);
                $(map[pp].form)
            }, function (msg) {

            }, []);
        }
    }

    function validateKittenBreeds(i) {
        console.log("validateKittenBreeds");
        let cat = getKitten(i);
        $(`#litter_kitten_${i} .w_ems`).hide();
        let breed = cat.ems.split(" ")[0];
        if (breedCache.indexOf(breed) >= 0) {
            if (i <= 1) {
                validateNewStructures();
            } else {
                validateKittenBreeds(i - 1);
            }
        }
        window.Util.breedExists(breed, function (e) {
            if (i <= 1) {
                validateNewStructures();
            } else {
                validateKittenBreeds(i - 1);
            }
        }, function (e) {
            $(`#litter_kitten_${i} .w_ems`).show();
        }, function (e) { console.log(e); })
    }

    function validateUniqueKitten(i) {
        console.log("ValidateUniqueKitten " + i);
        if (i == 0) {
            validateKittenBreeds(form_data.litterCount);
        }
        let cat = getKitten(i);
        $(`#litter_kitten_${i} .w_skrn`).hide();
        let digits = cat.registry_digits;
        if (jQuery.isNumeric(digits) && digits > 0) {
            window.Api.get("cat", { "registry_digits": digits }, function (e) {
                if (e.count === 0) {
                    if (i === 1) {
                        validateKittenBreeds(form_data.litterCount);
                    } else {
                        validateUniqueKitten(i - 1);
                    }
                } else {
                    $(`#litter_kitten_${i} .w_skrn`).show();
                }
            });
        } else {
            $(`#litter_kitten_${i} .w_skrn`).show();
        }
    }

    window.kitty = getKitten;


    function getLitterKittenForm(i, country = "IS", org = "KKÍ", num = 0000) {
        return `
<form id='litter_kitten_${i}'>
    <div style="clear:both;">            


        <div class="fullPageForm float-left">
<br><b>Kettlingur #${i}</b><br>
            <i>Nafn kettlings</i><br/>
            <i class="w_nafn warning">Köttur þarf að hafa nafn</i>                                                                                                              
            <input name='name' class="textinput" placeholder="Nafn" />
                        <br />

            <i>Skráninganúmer</i> <br/>       
            <i class="w_skrn warning">Skráninganúmer annaðhvort ógilt eða frátekið</i>

            <div>
                <input required name = 'country' value="${country}" class="tiny textinput" />
                <input required name= 'organization' value="${org}" class="tiny textinput" />
                <select required name='registration_class' class="tiny textinput">
                    <option>
                        RX
                            </option>
                    <option>
                        LO
                            </option>
                </select>
                <input required name='registry_digits' class="textinput normal" type="number" value="${num}" />
            </div>
            <i>EMS</i>   <br/>
            <i class="w_ems warning">Ógilt EMS gildi</i>

            <input required name='ems' class="textinput " placeholder="EMS" />
            <div class="radio-input">
                <i class="w_gender warning">Köttur þarf að hafa kyn</i>
                <i>Fress</i><input type="radio" name="gender" value="male" />
                <i>Læða</i><input type="radio" name="gender" value="female" />
            </div><br />
        </div>
        <div class="fullPageForm float-left">

            <br /><br>
            <i>Örmerki</i>           </br> 
            <i class="w_micro warning">Köttur þarf að vera örmerktur</i>

            <input required name='microchip' class="textinput" placeholder="0000000000000" /><br />

            <i>Kt. Eiganda (ef ekki ræktandi)</i>           </br> 
            <i class="w_ssn warning">Kennitala ekki lögleg</i><br>
            <input  name='owner' class="textinput form_kt" placeholder="" /><br />
            <input type='checkbox' name='foreign_owner' class='form_foreign_kt'/> 
            <i>Eigandi er án kennitölu</i><br>
            <i>Athugasemd</i>
            <input name='comment' type="text" class="textinput " placeholder="" />
        </div>

    </div>

</form>    
    `;
    }

    function getNewColorForm(i,Breed = "", color = "") {
        return `
        <form id='color_form_${i}'>
            <div class='fullPageForm float-left'>
                <i>Heiti litar</i><br>
                <input name='color' class='textinput'><br>
                <i>Lýsing litar</i><br>
                <input name='color_description' class='textinput'><br>
            </div>
            <div class='fullPageForm float-left'>
                <i>EMS kóði</i><br>
                <input name='color_short' class='normal textinput' value="${Breed} ${color}"><br>
                <i>Hópur (Group)</i><br>
                <input type=number name='color_description' class='normal textinput'>
            </div>
        </form>
    `;
    }

    function getNewOrginazationForm(i,acronym) {
        return `
        <form id='org_form_${i}'>
            <div class='fullPageForm float-left'>
                <i>Heiti félags</i>
                <input class="textinput normal" >
                <i>Skammstöfun félags</i>
                <input class="textinput normal" >
                <i>Upprunaland félags</i>
                ${countryForm}
            </div>
        </form>
    `;
    }

    function getNewPersonForm(i,kt) {
        return `
            <form class='person-form' id='person-form-${i}'>
            
            <div class='fullPageForm float-left'>
            <i>Nafn</i><br>
            <input name='name' class='textinput'><br>
            <i>Heimilisfang</i><br>
            <input name'address' class='textinput'><br>
            <i>Land</i><br>
            ${countryForm}

            <div class='fullPageForm float-left'>
            <i>Bæjarfélag</i><br/>
            <input name='city' class='textinput'>

            <i>Póstnúmer</i></br>
            <input name='postcode' class='normal textinput'>
</div>
            </div>

            <div class='fullPageForm float-left'>
            <i>Kennitala</i><br>
            <input name='ssn' readonly class='textinput readonly normal' value='${kt}'><br>
            <i>Sími</i><br>
            <input name='phone' class='normal textinput'><br>
            <i>Netfang</i><br>
            <input name='email' class='normal textinput'><br>


            </div>
            </form>
        `;
    }

    window.newPerson = getNewPersonForm;
});
