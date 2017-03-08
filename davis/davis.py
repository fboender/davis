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
        self.window.grid_rowconfigure(0, weight=1)
        self.window.grid_columnconfigure(0, weight=1)

        self.pane = PanedWindow(orient=VERTICAL)
        self.pane.grid(row=0, column=0, sticky="nesw", in_=self.window)
        self.pane.grid_rowconfigure(0, weight=1)
        self.pane.grid_columnconfigure(0, weight=1)

        tree_frame = self.mk_tree(self.pane)
        self.tree_fill(self.tree, obj)
        self.pane.add(tree_frame)

        value_viewer_frame = self.mk_value_viewer(self.pane)
        self.pane.add(value_viewer_frame)

    def mk_tree(self, master):
        tree_columns = (
            ("type", "Type"),
            ("value", "Value"),
        )

        frame = Frame(master, bg="#FF0000", bd=0)
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)

        tree = ttk.Treeview(frame,
                            columns=[c[0] for c in tree_columns],
                            selectmode=BROWSE)
        for c in tree_columns:
            tree.heading(c[0], text=c[1])
        tree.bind('<<TreeviewSelect>>', self.ev_treeitem_selected)
        tree.grid(row=0, column=0, sticky="nsew", in_=frame)

        scrollbar = Scrollbar(frame, command=tree.yview)
        scrollbar.grid(row=0, column=1, sticky="ns", in_=frame)
        tree['yscrollcommand'] = scrollbar.set

        self.tree = tree
        return frame

    def mk_value_viewer(self, master):
        frame = Frame(master, bg="#0000FF", bd=0)
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)

        text = Text(frame)
        text.grid(row=0, column=0, sticky="nsew", in_=frame)

        scrollbar = Scrollbar(frame, command=text.yview)
        scrollbar.grid(row=0, column=1, sticky="ns", in_=frame)
        text['yscrollcommand'] = scrollbar.set

        self.text = text
        return frame

    def tree_fill(self, tree, obj, parent=''):
        obj_type = type(obj).__name__

        if obj_type == 'dict':
            for val_name in sorted(obj.keys()):
                val_type = type(obj[val_name]).__name__
                val_value = obj[val_name]
                if val_type in recurse_types:
                    item_id = tree.insert(parent, 'end', text=val_name, values=(val_type, ))
                    self.item_values[item_id] = val_value
                    self.tree_fill(tree, val_value, item_id)
                else:
                    item_id = tree.insert(parent, 'end', text=val_name, values=(val_type, repr(val_value)))
                    self.item_values[item_id] = val_value
        elif obj_type in ('list', 'set', 'tuple'):
            i = 0
            for val_value in sorted(obj):
                val_type = type(val_value).__name__
                if val_type in recurse_types:
                    item_id = tree.insert(parent, 'end', text=i, values=(val_type))
                    self.tree_fill(tree, val_value, item_id)
                    self.item_values[item_id] = val_value
                else:
                    item_id = tree.insert(parent, 'end', text=i, values=(val_type, repr(val_value)))
                    self.item_values[item_id] = val_value
                i += 1
        else:
            item_id = tree.insert(parent, 'end', text=obj, values=(obj_type, ))
            self.item_values[item_id] = obj

    def ev_treeitem_selected(self, ev):
        item_id = self.tree.selection()[0]
        val_value = self.item_values[item_id]
        self.text.delete(1.0, END)
        self.text.insert("1.0", pprint.pformat(val_value))

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
