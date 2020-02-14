class Util {

    ///Existence tests
    breedExists(breed, existsCallback, doesNotExistCallback, errorCallback) {
        window.Api.get("ems", {}, function (e) {
            if (existsCallback) {
                existsCallback();
            }
        
        }, function (e) {
                if (e.error == "Resource does not exist") {
                    if (doesNotExistCallback) {
                        doesNotExistCallback();
                    }
                } else {
                    if (errorCallback) {
                        errorCallback();
                    }
                }
        },[breed], { 'offset': 1 });
    }
    emsColorExists(emsCode, existsCallback, doesNotExistCallback, errorCallback) {
        let b, c;
        b = emsCode.split(" ")[0];
        c = emsCode.split(" ").splice(1).join("_");
        window.Api.get("ems", {}, function (e) {
            if (existsCallback) {
                existsCallback();
            }

        }, function (e) {
            if (e.error == "Resource does not exist") {
                if (doesNotExistCallback) {
                    doesNotExistCallback();
                }
            } else {
                if (errorCallback) {
                    errorCallback();
                }
            }
        }, [b,c], { 'offset': 1 });
    }
    organizationAcronymExists(acronym, existsCallback, doesNotExistCallback, errorCallback) {
        let d = {};
        d.acronym = acronym;
        window.Api.get("organization", d, function (e) {
            if (e.count === 0) {
                if (doesNotExistCallback) {
                    doesNotExistCallback();
                } 
            }else {
                if (existsCallback) {
                    existsCallback();
                }
            }

        }, function (e) {
            if (e.error == "Resource does not exist") {
                if (doesNotExistCallback) {
                    doesNotExistCallback();
                }
            } else {
                if (errorCallback) {
                    errorCallback();
                }
            }
        }, [], { 'offset': 1 });
    }

    //Misc. validation tests
    ssn_valid(kt) {
        if (kt.length !== 10) {
            return false;
        }
        let d, m, a, cent;
        let rad, q, check, constant;
        d = kt.substr(0, 2);
        m = kt.substr(2, 2);
        a = kt.substr(4, 2);
        rad = kt.substr(6, 2);
        q = kt.substr(8, 1);
        cent = kt.substr(9, 1);
        check = kt.substr(0, 8);
        constant = "32765432";

        cent = (cent == 8 || cent == 9) ? "1"+cent : "2"+cent;
        let date = cent + a + "-" + m + "-" + d;
        date = moment(date, 'YYYY-MM-DD');
        if (!date.isValid()) {
            return false;
        }
        if (rad < 20) {
            return false;
        }
        let sum = 0;
        for (let i = 0; i < constant.length; i++) {
            sum += check[i] * constant[i];
        }
        let r = 11 - sum % 11;
        if (r !== parseInt(q)) {
            return false;
        }
        return true;
    }

    ///Form finders
    forms_countrySelection(callback) {
        let formMaker = function (msg) {
            let form = "<select class='textinput' name='country'>";
            for (let nation of msg.data) {
                let c = nation.code;
                let n = nation.name;
                form += `<option value="${c}">${n}</option>`;
            }
            form += "</select>";
            callback(form);
        }
        this.formLoader("countryCodes", formMaker);
    }
    formLoader(form, callback) {
        let url;
        switch (form) {
            case "countryCodes": {
                url = "/static/shared/AllCountries.json";
                break;
            }
            default: {
                throw "NO FORM WITH NAME " + form;
            }
        }
        $.ajax({
            method: "GET",
            url: url
        }).done(function (msg) {
            if (callback) {
                callback(msg);
            }
        });
    }
} 


