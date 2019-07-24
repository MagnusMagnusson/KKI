//Handles all external modules / forms we might require.
class ModuleManager {
    constructor() {
        this.modules = {};
        this.moduleQueue = [];
        this.messageQueue = {};
        this.setupHandlers();
        this.loadedScripts = [];
    }


    getMessage(module) {
        if (this.messageQueue[module]) {
            if (this.messageQueue[module].length > 0) {
                return this.messageQueue[module].pop();
            }
        }
    }
    //Fetches a module via API: if it does not already exist in the DOM.
    loadModule(module, caller = null, callback = null) {
        if (caller) {
            let backlog = [caller, callback];
            this.moduleQueue.push(backlog);
        }
        if (this.modules[module]) {
            this.modules[module].show();
            this.modules[module].activate();
            $("#modules").addClass("visible");
        }
        else {
            window.Api.getModule(module,this.registerNewModule);
        }
    }

    activateModule(module) {
        if (this.modules[module]) {
            this.modules[module].activate();
        } else {
            throw "No module named " + module;
        }
    }

    //Close the module. If there are other modules currently waiting for data, resume the most recent one
    closeModule(module,success = false) {
        if (this.modules[module]) {
            this.modules[module].close();
        }
        if (this.moduleQueue.length > 0) {
            this.resumeModule(success);
        } else {
            $("#modules").removeClass("visible");
        }
    }


    saveModule(module) {
        if (this.modules[module]) {
            this.modules[module].save();
        }
    }

    saveSuccess(module, message = null, result=null) {
        if (this.modules[module]) {
            if (message && this.moduleQueue.length > 0) {
                let topModule = this.moduleQueue[this.moduleQueue.length - 1].name;
                if (!this.messageQueue[topModule]) {
                    this.messageQueue[topModule] = [];
                }
                this.messageQueue[topModule].push(message);
            }
            this.closeModule(module, true);
            var event = new CustomEvent("module-success", {
                detail: {
                    module,
                    message,
                    result
                }
            });
            console.log(message, result);
            document.dispatchEvent(event);
        }
    }

    //Resume a module.
    resumeModule(success) {
        var nextModule = this.moduleQueue.pop();
        nextModule.resume(success);
    }

    sendMessage(sendee, message) {
        if (!this.messageQueue[sendee]) {
            this.messageQueue[sendee] = [];
        }
        if (message) {
            this.messageQueue[sendee].push(message);
        }
    }

    //A module wishes for information for a different module. Put it on the stack and load the requested module
    requestData(caller, module, callback, message = null) {
        console.log(caller + " has requested data from " + module);
        if (!this.messageQueue[module]) {
            this.messageQueue[module] = [];
        }
        if (message) {
            this.messageQueue[module].push(message);
        }
        this.modules[caller].pendingAction = callback;
        this.moduleQueue.push(this.modules[caller]);
        this.loadModule(module);
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

    registerModuleHandler(module, name, handler) {
        if (this.modules[module]) {
            this.modules[module].registerHandler(name, handler);
        } else {
            console.log(this.modules);
            throw "No module named " + module;
        }
    }

    setupHandlers() {
        let t = this;

        $(".module-button").on("click", function (e) {
            if ($(".module:visible").length == 0) {
                let module = $(this).data("module");
                if ($(this).data("message")) {
                    window.ModuleManager.sendMessage(module, $(this).data("message"));
                }
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

    resume(success) {
        this.show();
        if (this.pendingAction) {
            if (success) {
                let msg = window.ModuleManager.getMessage(this.name);
                this.pendingAction(msg);
            }
            this.pendingAction = null;
        }
    }

    save(callback) {
        if (this.handler['save']) {
            this.handler['save'](callback);
        } else {
            throw "Module " + this.name + " must register a save handler";
        }
    }

    activate(callback) {
        if (this.handler['activate']) {
            this.handler['activate'](callback);
        } else {
            throw "Module " + this.name + " must register an activation handler";
        }

    }

    registerHandler(name, handler) {
        this.handler[name] = handler;
    }
}