# odoo-features
This repo contains some odoo features that are directly not available in odoo community versions

# `many2many_field`  - Many2many field option
* This module exposed an option called initial_view so that we can control if we
want to open search view or form view whenever we are clicking Add a line in tree view
* Example: 
```
<field name="worker_ids" widget="many2many"
    options="{'initial_view': 'form'}">
```
* Above example will open up a form view for the worker_ids model instead of default
search view
* You were wondering why not just use one2many, well in one2many you can not save
the record as soon as you create it you have to save the parent form for it but
in many2many you can create the record as soon as you hit Save & Close.


# `odoo_create_button` - Add different action in odoo default create button

`Add context key create_do_action so that we can perform a 
do_action instead of default create procedure of odoo,
it helps in cases where we want a different form view when we
hit create in the list/kanban view
`

- [x] Work in list view
- [ ] work in kanban view
- [ ] work in form view



# `extra_control_panel_buttons` - Add extra buttons in Control panel

#### How it works

* Add attribute `extra_cp_buttons` on the kanban tag with the id of the qweb that you want to render
  on the control panel left with class o_cp_buttons
* Or you can add `extra_cp_buttons` in context of the action, in list view extra attributes
are not allowed in tree tag
* Define the buttons in the format as you do in form xml with type and name
* Supported button type are `object` only

#### TODO

- [ ] Add the same in form
- [ ] Add in list view etc 
- [ ] Add in kanban view etc 
- [ ] Add button type action also for buttons
- [ ] Add possibility to add modifiers on the buttons,
- [ ] Add possibility to add groups on the buttons,

#### Example

```xml

<kanban limit="40" extra_cp_buttons="gallery.buttons">
</kanban>

```
