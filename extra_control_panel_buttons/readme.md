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
- [x] Add in list view etc 
- [x] Add in kanban view etc 
- [ ] Add button type action also for buttons
- [ ] Add possibility to add modifiers on the buttons,
- [ ] Add possibility to add groups on the buttons,

#### Example

```xml

<kanban limit="40" extra_cp_buttons="gallery.buttons">
</kanban>

```
