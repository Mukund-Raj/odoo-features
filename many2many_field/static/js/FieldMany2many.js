odoo.define('many2many_field.FieldMany2many.options', function(require){

var FieldMany2many = require('web.relational_fields').FieldMany2Many;
var dialogs = require('web.view_dialogs');
var core = require('web.core');
var _t = core._t;

FieldMany2many.include({
    onAddRecordOpenDialog: function () {
        var self = this;
        var domain = this.record.getDomain({fieldName: this.name});

        // initial_view => search/form , opens the search view or the form view
        new dialogs.SelectCreateDialog(this, {
            res_model: this.field.relation,
            domain: domain.concat(["!", ["id", "in", this.value.res_ids]]),
            context: _.extend(this.record.getContext(this.recordParams), this.value.getContext()),
            title: _t("Add: ") + this.string,
            no_create: this.nodeOptions.no_create || !this.activeActions.create,
            initial_view: this.nodeOptions?.initial_view || 'search',
            fields_view: this.attrs.views.form,
            kanban_view_ref: this.attrs.kanban_view_ref,
            on_selected: function (records) {
            var resIDs = _.pluck(records, 'id');
            var newIDs = _.difference(resIDs, self.value.res_ids);
            if (newIDs.length) {
                var values = _.map(newIDs, function (id) {
                    return {id: id};
                });
                self._setValue({
                    operation: 'ADD_M2M',
                    ids: values,
                });
            }
        }
    }).open();
},
});
})