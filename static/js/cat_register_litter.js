$(document).ready(function (e) {
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

        let kitten = {};
        for (let field of formObject) {
            kitten[field.name] = field.value;
        }
        return kitten;
    }

    function validate_postform() {
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
        }
        return true;
    }

    function validate_preform() {
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
                console.log(regnr)
                $(`${form_id} .w_skrnr`).show();
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
            'name':text
        };

        window.Api.find("cattery", d, function (e) {
            if (e.results.length == 0) {
                return;
            }
            $("#lr_cattery_registry_results .result-box-list").empty();
            for (res of e.results.slice(0,10)) {
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

            $("#lr_pairing").hide();
            $("#lr_kitten_section").show();
        } else {
            preform_errors_show();
        }
    });

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
            console.log(digits);
            console.log(kitten);
            if (regDigits.indexOf(digits) >= 0) {
                valid = false;
                console.log(regDigits);
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

        console.log(newOrgs);
        console.log(newColors);
    }

    function validateNewStructures() {
        let confirmationRequestsWaiting;
        let confirmationRequestId = Math.floor(Math.random() * Math.pow(2, 32));
        let currentId = confirmationRequestId;
        let colors = [];
        let orginizations = [];
        newColors = [];
        newOrgs = [];

        for (let i = 1; i <= form_data.litterCount; i++) {
            let k = getKitten(i);
            let ems = k.ems;
            let org = k.organization;
            if (colors.indexOf(ems) === -1) {
                colors.push(ems);
            }
            if (orginizations.indexOf(org) === -1) {
                orginizations.push(org);
            }
        }
        confirmationRequestsWaiting = colors.length + orginizations.length;
        for (let c of colors) {
            window.Util.emsColorExists(c, function (e) {
                if (currentId === confirmationRequestId) {
                    confirmationRequestsWaiting--;
                    if (confirmationRequestsWaiting === 0) {
                        showNewStructures();
                    }
                }
            }, function (e) {
                if (currentId === confirmationRequestId) {
                    newColors.push(c);
                    confirmationRequestsWaiting--;
                    if (confirmationRequestsWaiting === 0) {
                        showNewStructures();
                    }
                }
            }, null);
        }
        for (let o of orginizations) {
            window.Util.organizationAcronymExists(o, function (e) {
                if (currentId === confirmationRequestId) {
                    confirmationRequestsWaiting--;
                    if (confirmationRequestsWaiting === 0) {
                        showNewStructures();
                    }
                }
            }, function (e) {
                if (currentId === confirmationRequestId) {
                    newOrgs.push(o);
                    confirmationRequestsWaiting--;
                    if (confirmationRequestsWaiting === 0) {
                        showNewStructures();
                    }
                }
            }, null);
        }
    }

    function validateKittenBreeds(i) {
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
});

function getLitterKittenForm(i, country = "IS", org = "KKI", num = 0000) {
    return `
<form id='litter_kitten_${i}'>
    <div style="clear:both;">            


        <div class="fullPageForm float-left">
<br><b>Kettlingur #${i}</b><br>
            <i>Nafn kettlings</i><br/>
            <i class="w_nafn warning">Köttur þarf að hafa nafn</i><br />
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
                    <option>
                        HUS
                            </option>
                </select>
                <input required name='registry_digits' class="textinput normal" type="number" value="${num}" />
            </div>
            <i>EMS</i>   <br/>
            <i class="w_ems warning">Ógilt EMS gildi</i>

            <input required name='ems' class="textinput " placeholder="EMS" />
        </div>
        <div class="fullPageForm float-left">

            <br /><br>
            <div class="radio-input">
                <i class="w_gender warning">Köttur þarf að hafa kyn</i><br/>
                <i>Fress</i><input type="radio" name="gender" value="male" />
                <i>Læða</i><input type="radio" name="gender" value="female" />
            </div><br />
            <i>Örmerki</i>           </br> 
            <i class="w_micro warning">Köttur þarf að vera örmerktur</i>

            <input required name='microchip' class="textinput" placeholder="0000000000000" /><br />
            <i>Athugasemd</i>
            <input name='comment' type="text" class="textinput " placeholder="" />
        </div>

    </div>

</form>    
    `;
}

function getNewColorForm(Breed = "", color = "") {
    let cString = color.replace(" ", "_");
    return 
    `
        <form id='color_form_
    `;
}