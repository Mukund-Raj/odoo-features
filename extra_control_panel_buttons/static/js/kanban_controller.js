odoo.define('extra_control_panel_buttons.KanbanController', function(require){

    var KanbanController = require('web.KanbanController');
    var core = require('web.core');
    var qweb = core.qweb;
    var Context = require('web.Context');
    var session = require("web.session");

    KanbanController.include({
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

        renderButtons: function ($node) {
            var self = this;
            this._super.apply(this, arguments);
            if(self.renderer.arch.attrs.extra_cp_buttons){
                this.$extra_buttons = $(qweb.render(self.renderer.arch.attrs.extra_cp_buttons));
                this.$extra_buttons.appendTo($node);
                this.$extra_buttons.on('click', 'button', this.onClickExtraCpButtons.bind(this));
            }
        }
    })
})