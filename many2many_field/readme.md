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
