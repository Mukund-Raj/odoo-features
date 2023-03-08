odoo.define('views.create_buttons', function(require){

    var core = require('web.core');
    var qweb = core.qweb;
    var Context = require('web.Context');
    var session = require("web.session");

    var ListController = require('web.ListController');
    ListController.include({
        _onCreateRecord: function (ev) {
            // if `create_do_action` is in context then do tht
            if(this.initialState.context?.create_do_action){
                this.do_action(this.initialState?.context.create_do_action);
            }
            else{
                this._super.apply(this,arguments);
            }
        }
    });
})