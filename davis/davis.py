#!/usr/bin/env python

from Tkinter import *
import ttk
import json
import pprint

recurse_types = ('dict', 'list', 'tuple', 'set')

class MainInterface(object):
    def __init__(self, obj):
        self.obj = obj
        self.item_values = {}

        self.window = Tk()
        self.window.title("Python Data Visualizer")
        self.window.bind("<Escape>", lambda e: e.widget.quit())
        self.window.geometry('700x500')

        scrollbar = Scrollbar(self.window)
        scrollbar.pack(side=RIGHT, fill=Y)

        tree_columns = (
            ("type", "Type"),
            ("value", "Value"),
        )
        self.tree = ttk.Treeview(self.window,
                                 columns=[c[0] for c in tree_columns],
                                 yscrollcommand=scrollbar.set)
        for c in tree_columns:
            self.tree.heading(c[0], text=c[1])
        self.tree.pack(side=TOP, expand=YES, fill=BOTH)
        self.tree.bind('<Double-1>', self.ev_treeitem_doubleclicked)

        self.tree_fill(obj)

    def run(self):
        self.window.mainloop()

    def tree_fill(self, obj, parent=''):
        obj_type = type(obj).__name__

        if obj_type == 'dict':
            for val_name in sorted(obj.keys()):
                val_type = type(obj[val_name]).__name__
                val_value = obj[val_name]
                if val_type in recurse_types:
                    item_id = self.tree.insert(parent, 'end', text=val_name, values=(val_type, ))
                    self.item_values[item_id] = val_value
                    self.tree_fill(val_value, item_id)
                else:
                    item_id = self.tree.insert(parent, 'end', text=val_name, values=(val_type, repr(val_value)))
                    self.item_values[item_id] = val_value
        elif obj_type in ('list', 'set', 'tuple'):
            i = 0
            for val_value in sorted(obj):
                val_type = type(val_value).__name__
                if val_type in recurse_types:
                    item_id = self.tree.insert(parent, 'end', text=i, values=(val_type))
                    self.tree_fill(val_value, item_id)
                    self.item_values[item_id] = val_value
                else:
                    item_id = self.tree.insert(parent, 'end', text=i, values=(val_type, repr(val_value)))
                    self.item_values[item_id] = val_value
                i += 1
        else:
            item_id = self.tree.insert(parent, 'end', text=obj, values=(obj_type, ))
            self.item_values[item_id] = obj

    def ev_treeitem_doubleclicked(self, ev):
        item_id = self.tree.selection()[0]
        val_value = self.item_values[item_id]
        v = ViewValueInterface(val_value)


class ViewValueInterface:
    def __init__(self, value):
        self.window = Toplevel()
        self.window.title("Value")
        self.window.bind("<Escape>", lambda e: self.window.destroy())

        scrollbar = Scrollbar(self.window)
        scrollbar.pack(side=RIGHT, fill=Y)

        self.text = Text(self.window, width=80, height=25, yscrollcommand=scrollbar.set)
        self.text.pack(side=TOP, expand=YES, fill=BOTH)
        self.text.insert('1.0', pprint.pformat(value))

    def run(self):
        self.window.mainloop()


def vis(obj):
    main_interface = MainInterface(obj)
    main_interface.run()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        fname = sys.argv[1]
        with open(fname, 'r') as f:
            contents = f.read()
    else:
        contents = sys.stdin.read()

    decoded = None
    errs = []

    if not decoded:
        try:
            decoded = json.loads(contents)
        except Exception as e:
            errs.append( ('json', str(e)) )

    if not decoded:
        try:
            decoded = eval(contents)
        except Exception as e:
            errs.append( ('python', str(e)) )

    if decoded:
        vis(decoded)
    else:
        sys.stderr.write("Couldn't decode. Tried:\n")
        for err_causer, err_cause in errs:
            sys.stderr.write("  {0}: {1}\n".format(err_causer, err_cause))
        sys.exit(1)
