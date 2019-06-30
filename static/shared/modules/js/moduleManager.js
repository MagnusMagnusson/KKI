//Handles all external modules / forms we might require.
class ModuleManager {
    constructor() {
        this.modules = {};
        this.moduleQueue = [];
        this.messageQueue = [];
        this.setupHandlers();
        this.loadedScripts = [];
    }

    //Fetches a module via API: if it does not already exist in the DOM.
    loadModule(module, caller = null, callback = null) {
        if (caller) {
            let backlog = [caller, callback];
            this.moduleQueue.push(backlog);
        }
        if (this.modules[module]) {
            this.modules[module].show();
            $("#modules").addClass("visible");
        }
        else {
            window.Api.getModule(module,this.registerNewModule);
        }
    }

    //Close the module. If there are other modules currently waiting for data, resume the most recent one
    closeModule(module) {
        if (this.modules[module]) {
            this.modules[module].close();
        }
        if (this.moduleQueue.length > 0) {
            this.resumeModule();
        }
    }

    //Resume a module.
    resumeModule() {
        var nextModule = this.moduleQueue.pop();
        nextModule.resume();
    }

    //A module wishes for information for a different module. Put it on the stack and load the requested module
    requestData(caller, module) {
        this.moduleQueue.push(this.modules[caller]);
        this.loadModule(module);
        console.log(caller + " has requested data from " + module);
    }

    //the API has returned our requested module. Insert it in to the DOM and our datastores
    registerNewModule(msg) {
        let t = window.ModuleManager;
        $(".module.popup").hide();
        $("#modules").append(msg.html);
        $("#modules").addClass("visible");
        let guiModule = $(".module[data-module='" + msg.name + "']");
        let newModule = new Module(msg.name, guiModule);
        t.modules[msg.name] = newModule;
        for (let script of msg.js) {
            if (!t.loadedScripts.includes(script)) {
                t.loadedScripts.push(script);
                $.getScript(script);
            } else {
                console.log("Blocked loading same script twice");
            }
        }
    }

    setupHandlers() {
        let t = this;

        $(".module-button").on("click", function (e) {
            if ($(".module:visible").length == 0) {
                let module = $(this).data("module");
                t.loadModule(module);
            }
        });
    }
}

class Module {
    constructor(name, gui) {
        this.gui = gui;
        this.handler = {};
        this.name = name;
    }

    close() {
        console.log(this.gui);
        $(this.gui).hide();
    }

    show() {
        $(this.gui).show();
    }

    resume() {
        this.show();
    }

    save(callback) {
        if (this.handler['save']) {
            this.saveHandler(callback);
        } else {
            throw "Module " + this.name + " must register a save handler";
        }
    }

    registerHandler(name, handler) {
        this.handler[name] = handler;
    }
}