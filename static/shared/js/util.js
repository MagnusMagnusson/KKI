class Util {

    breedExists(breed, existsCallback, doesNotExistCallback, errorCallback) {
        window.Api.get("ems", {}, function (e) {
            if (existsCallback) {
                existsCallback();
            }
        
        }, function (e) {
            console.log(e);
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
        console.log(c);
        window.Api.get("ems", {}, function (e) {
            if (existsCallback) {
                existsCallback();
            }

        }, function (e) {
            console.log(e);
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
            console.log(e);
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
}