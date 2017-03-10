#!/usr/bin/env python

import json
import pprint
try:
    from Tkinter import *  # Python 2
    import ttk
except ImportError:
    from tkinter import *  # Python 3
    from tkinter import ttk


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

        tree_view_frame = self.mk_tree_view(self.pane)
        self.tree_set_children('', obj)
        self.pane.add(tree_view_frame)

        value_view_frame = self.mk_value_view(self.pane)
        self.pane.add(value_view_frame)

    def mk_tree_view(self, master):
        """
        Construct the tree view frame.
        """
        tree_columns = (
            ("type", "Type"),
            ("value", "Value"),
        )

        frame = Frame(master)
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)

        tree = ttk.Treeview(frame,
                            columns=[c[0] for c in tree_columns],
                            selectmode=BROWSE)
        for c in tree_columns:
            tree.heading(c[0], text=c[1])
        tree.bind('<<TreeviewSelect>>', self.ev_treeview_select)
        tree.bind('<<TreeviewOpen>>', self.ev_treeview_open)
        tree.grid(row=0, column=0, sticky="nsew", in_=frame)

        scrollbar = Scrollbar(frame, command=tree.yview)
        scrollbar.grid(row=0, column=1, sticky="ns", in_=frame)
        tree['yscrollcommand'] = scrollbar.set

        self.tree = tree
        return frame

    def mk_value_view(self, master):
        """
        Construct the value viewer frame.
        """
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

    def ev_treeview_select(self, ev):
        """
        <<TreeviewSelect>> event. When an item in the tree is selected, we
        update the Value view with a representation of the value that was
        selected.
        """
        item_id = self.tree.selection()[0]
        val_value = self.item_values[item_id]
        self.text.delete(1.0, END)
        self.text.insert("1.0", pprint.pformat(val_value))

    def ev_treeview_open(self, ev):
        """
        <<TreeviewOpen>> event. When an item in the tree is opened, we delete
        the placeholder in the tree and insert the child values of the selected
        item in the tree under the item.
        """
        item_id = self.tree.selection()[0]
        obj = self.item_values[item_id]
        self.tree_set_children(item_id, obj)

    def tree_set_row(self, obj_name, obj, parent='', depth=0):
        """
        Insert a row into the tree, determining the columns by the type of the
        object being added. A placeholder is added under the new item which
        makes it openable.
        """
        obj_type = type(obj).__name__
        obj_val = repr(obj)

        # Add a row to the tree
        if obj_type == 'dict':
            item_id = self.tree.insert(parent, 'end', text=obj_name, values=(obj_type, ))
            self.item_values[item_id] = obj
        elif obj_type in ('list', 'tuple', 'set'):
            item_id = self.tree.insert(parent, 'end', text=obj_name, values=(obj_type, ))
            self.item_values[item_id] = obj
        elif obj_type in ('str', 'unicode', 'int', 'float', 'bool'):
            item_id = self.tree.insert(parent, 'end', text=obj_name, values=(obj_type, obj_val))
            self.item_values[item_id] = obj
        else:
            item_id = self.tree.insert(parent, 'end', text=obj_name, values=(obj_type, obj_val))
            self.item_values[item_id] = obj

        # Add a placeholder so it looks like the tree can be opened, but in
        # reality there's nothing under it. We fill it on demand.
        #self.tree_recurse(obj_name, obj, item_id, depth+1)
        self.tree.insert(item_id, 'end', text="placeholder")

    def tree_set_children(self, item_id, obj):
        """
        Delete all children (including placeholders) under an item in the tree
        and add the children of obj in the tree.
        """
        children = self.tree.get_children(item_id)
        self.tree.delete(*children)

        for child_obj_name, child_obj in self.get_child_objs(obj):
            self.tree_set_row(child_obj_name, child_obj, item_id)

    def get_child_objs(self, obj):
        """
        Return a list of children of 'obj' and their types. Various things are
        determined based on the type of 'obj'.
        """
        obj_type = type(obj).__name__
        child_objs = []

        if obj_type == 'dict':
            for child_obj_name in sorted(obj.keys()):
                child_obj = obj[child_obj_name]
                child_objs.append((child_obj_name, child_obj))
        elif obj_type in ('list', 'tuple'):
            for i in range(len(obj)):
                child_obj_name = str(i)
                child_obj = obj[i]
                child_objs.append((child_obj_name, child_obj))
        elif obj_type == 'set':
            for child_obj in obj:
                child_obj_name = ''
                child_objs.append((child_obj_name, child_obj))
        else:
            for child_obj_name in dir(obj):
                child_obj = getattr(obj, child_obj_name)
                child_objs.append((child_obj_name, child_obj))

        return child_objs

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
