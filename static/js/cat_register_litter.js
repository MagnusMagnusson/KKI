$(document).ready(function (e) {
    //Search result population. 
    $("#lr_cattery_registry").on("input", function (e) {
        let text = $(this).val();
        if (text.length < 3) {
            return;
        }

        let d = {
            'type': 'cattery',
            'term': 'name',
            'value': text
        };
        window.Api.find(d, function (e) {
            if (e.results.length == 0) {
                return;
            }
            $("#lr_cattery_registry_results .result-box-list").empty();
            for (res of e.results.slice(0,10)) {
                let cattery = res[1];
                li = $(`<li>${cattery.name}</li>`);
                $("#lr_cattery_registry_results .result-box-list").append(li);

                $(li).on("click touchstart", function (e) {
                    $("#lr_cattery_registry").val(cattery.name);
                    $("#lr_cattery_registry_id").val(cattery.id);
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

        let d = {}
        d['json'] = JSON.stringify({
            'type': 'cat',
            'term': 'reg_full',
            'value': text,
            'filters': {
                'gender': fill,
                'neutered':false,
            }
        });

        window.Api.find(d, function (e) {
            if (e.results.length == 0) {
                return;
            }
            $(`#lr_${fill}_registry_results .result-box-list`).empty();
            for (res of e.results.slice(0, 10)) {
                console.log(res);
                let cat = res[1];
                li = $(`<li>${cat.name}</li>`);
                $(`#lr_${fill}_registry_results .result-box-list`).append(li);

                $(li).on("click touchstart", function (e) {
                    $(`#lr_${fill}_registry`).val(cat.registry);
                    $(`#lr_${fill}_registry_name`).val(cat.fullName);
                    $(`#lr_${fill}_registry_ems`).val(cat.ems);
                    $(`#lr_${fill}_registry_micro`).val(cat.microchip);
                    $(`#lr_${fill}_registry_birthdate`).val(cat.birthdate);
                    $(`#lr_${fill}_registry_id`).val(cat.id);
                    $(`#lr_${fill}_registry_results`).hide();
                });
            }
            $(`#lr_${fill}_registry_results`).show();
        });
    });

    $("#lr_next_button").on("click touchstart", function (e) {
        e.preventDefault();
        let littersize = parseInt($("input[name='litter_amount']").val());
        if (littersize > 0) {

            for (let i = 0; i < littersize; i++) {
                let formHtml = getLitterKittenForm(1 + i);
                let formdiv = $(formHtml);
                $("#lr_kitten_formlist").append(formdiv);
                window.Api.getNextRegNr(function (e) {
                    let nr = i + e.result;
                    $(formdiv).find(`input[name='kitten_reg_nr`).val(nr);
                })
            }

            $("#lr_pairing").hide();
            $("#lr_kitten_section").show();
        }
    });

    $("#confirm_litter_button").on("click touchstart", function (e) {
        let littersize = parseInt($("input[name='litter_amount']").val());
        for (let i = 1; i <= littersize; i++) {
            kitten = getKitten(i);
            if (kitten === false) {
                continue;
            }
            string = JSON.stringify(kitten);
            kitten = {};
            kitten['data'] = string;
            if (typeof kitten.data.id !== 'undefined') {
                console.log(kitten.data.id)
                console.log("Imp "+i+"detected!");
            } else {
                window.Api.submitCat(kitten, function (msg) {
                    if (msg.success) {
                        let formName = "#litter_kitten_" + i;
                        $(formname).find("input[name='id']").val(msg.result.id);
                    }
                });
            }
        }
    });
});

function getLitterKittenForm(i, country = "IS", org = "KKI", num = 0000) {
    return `
<form id='litter_kitten_${i}'>
    <div style="clear:both;">            
<div class='warning'>Köttur var ekki skráður, vinsamlegast athugaðu að allir reitir séu gildir</div>


        <div class="fullPageForm float-left">
<br><b>Kettlingur #${i}</b><br>
            <i>Nafn kettlings</i><br />
            <input name='kitten_name' class="textinput" placeholder="Nafn" /><br />
            <i>Skráninganúmer</i>                
            <input name='id' class='hidden readonly' value="">

            <div>
                <input required name = 'kitten_country' value="${country}" class="tiny textinput" />
                <input required name= 'kitten_org' value="${org}" class="tiny textinput" />
                <select required name='kitten_class' class="tiny textinput">
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
                <input required name='kitten_reg_nr' class="textinput normal" type="number" value="${num}" />
            </div>
            <i>EMS</i>
            <input required name='kitten_ems' class="textinput " placeholder="EMS" />
        </div>
        <div class="fullPageForm float-left">
            <br /><br>
            <div class="radio-input">
                <i>Fress</i><input type="radio" name="kitten_gender" value="male" />
                <i>Læða</i><input type="radio" name="kitten_gender" value="female" />
            </div><br />
            <i>Örmerki</i>
            <input required name='kitten_microchip' class="textinput" placeholder="0000000000000" /><br />
            <i>Athugasemd</i>
            <input name='kitten_comment' type="text" class="textinput " placeholder="" />
        </div>

    </div>

</form>    
    `;
}

function getKitten(i) {
    let formName = "#litter_kitten_" + i;
    formObject = $(formName).serializeArray();
    if (formObject.length < 10) {
        return false;
    }

    let cattery = $("#lr_cattery_registry_id").val();
    formObject.push({ 'name': 'cattery', 'value': cattery });
    let sire = $("#lr_sire_registry_id").val();
    formObject.push({ 'name': 'sire', 'value': sire });
    let dam = $("#lr_dam_registry_id").val();
    formObject.push({ 'name': 'dam', 'value': dam });
    let birth = $("#lr_birthdate").val();
    formObject.push({ 'name': 'birth', 'value': birth });

    let kitten = {};
    for (let field of formObject) {
        let name = field.name.replace("kitten_", "");
        kitten[name] = field.value; 
    }
    return kitten;
}