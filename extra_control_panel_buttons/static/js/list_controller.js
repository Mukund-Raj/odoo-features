odoo.define('extra_control_panel_buttons.ListController', function(require){

    var ListController = require('web.ListController');
    var core = require('web.core');
    var qweb = core.qweb;
    var Context = require('web.Context');
    var session = require("web.session");

    ListController.include({
        get_button_attrs: function(ev){
            var button = $(ev.currentTarget);
            var node = {
                          "tag": "button",
                          'type': button.attr('type'),
                          'name': button.attr('name'),
                          'context': button.attr('context'),
                          "attrs": {
                            "name": button.attr('name'),
                            "string": button.attr('string'),
                            "type": button.attr('type'),
                            "class": button.attr('class'),
                            "modifiers": {},
                            "options": {}
                          },
                          "children": []
                        }
            return node;
        },

        onClickExtraCpButtons: function(ev){
            var actionData = this.get_button_attrs(ev);
            // handle button type action
            if(actionData?.type == 'action'){
                this.do_action(actionData?.name);
                return;
            }
            var context = new Context(_.extend({}, session.user_context, actionData.context|| {}));
            var self = this;
            this._rpc({
                route: '/web/dataset/call_button',
                params: {
                    args: [],
                    kwargs: {context: context.eval()},
                    method: actionData.name,
                    model: this.modelName,
                },
            }).then(function(action){
                self.do_action(action);
            });
//            this.trigger_up('button_clicked', {
//                    attrs: this.get_button_attrs(ev),
//            });
        },

        has_extra_cp_buttons: function(){
            if(this.renderer.arch.attrs?.extra_cp_buttons){
                return true;
            }
            else if(this.renderer.state.context?.extra_cp_buttons){
                return true;
            }
            return false;
        },

        get_extra_cp_button_qweb: function(){
            if(this.renderer.arch.attrs?.extra_cp_buttons){
                return $(qweb.render(this.renderer.arch.attrs.extra_cp_buttons));
            }
            else if(this.renderer.state.context?.extra_cp_buttons){
                return $(qweb.render(this.renderer.state.context.extra_cp_buttons));
            }
        },

        renderButtons: function ($node) {
            var self = this;
            this._super.apply(this, arguments);
            // check if this list has extra_cp_buttons in context
            if(this.has_extra_cp_buttons()){
                this.$extra_buttons = this.get_extra_cp_button_qweb();
                this.$extra_buttons.appendTo($node);
                this.$extra_buttons.on('click', 'button', this.onClickExtraCpButtons.bind(this));
            }
        }
    })
})