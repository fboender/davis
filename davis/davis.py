#!/usr/bin/env python

import json
import pickle
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
        self.show_magic = IntVar()
        self.show_raw_value = IntVar()

        self.window.title("Python Data Visualizer")
        self.window.bind("<Escape>", lambda e: e.widget.quit())
        self.window.geometry('700x500')
        self.window.grid_rowconfigure(0, weight=1)
        self.window.grid_columnconfigure(0, weight=1)

        self.pane = PanedWindow(orient=VERTICAL)
        self.pane.grid(row=0, column=0, sticky="nesw", in_=self.window)
        self.pane.grid_rowconfigure(0, weight=1)
        self.pane.grid_columnconfigure(0, weight=1)

        options_frame = self.mk_options(self.pane)
        self.pane.add(options_frame)

        tree_view_frame = self.mk_tree_view(self.pane)
        self.tree_set_children('', obj)
        self.pane.add(tree_view_frame)

        value_view_frame = self.mk_value_view(self.pane)
        self.pane.add(value_view_frame)

    def mk_options(self, master):
        frame = Frame(master, border=10)
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(1, weight=1)

        l = Label(master, text="Show magic methods")
        l.grid(row=0, column=0, sticky="e", in_=frame)
        c = Checkbutton(master, text="", variable=self.show_magic)
        c.grid(row=0, column=1, sticky="w", in_=frame, pady=5)

        l = Label(master, text="Show raw value")
        l.grid(row=1, column=0, sticky="e", in_=frame)
        c = Checkbutton(master, text="", variable=self.show_raw_value)
        c.grid(row=1, column=1, sticky="w", in_=frame, pady=5)

        l = Label(master, text="Path to item: ")
        l.grid(row=2, column=0, sticky="e", in_=frame)
        e = Entry(master)
        e.grid(row=2, column=1, sticky="nsew", in_=frame, pady=5)
        self.accessor = e

        return frame

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
        notebook = ttk.Notebook(master)
        frame_value = ttk.Frame(notebook)
        frame_docstr = ttk.Frame(notebook)
        frame_value.grid_rowconfigure(0, weight=1)
        frame_value.grid_columnconfigure(0, weight=1)
        frame_docstr.grid_rowconfigure(0, weight=1)
        frame_docstr.grid_columnconfigure(0, weight=1)
        notebook.add(frame_value, text='Value')
        notebook.add(frame_docstr, text='Docstring')

        text_value = Text(frame_value)
        text_value.grid(row=0, column=0, sticky="nsew", in_=frame_value)
        scrollbar = Scrollbar(frame_value, command=text_value.yview)
        scrollbar.grid(row=0, column=1, sticky="ns", in_=frame_value)
        text_value['yscrollcommand'] = scrollbar.set
        self.text_value = text_value

        text_docstr = Text(frame_docstr)
        text_docstr.grid(row=0, column=0, sticky="nsew", in_=frame_docstr)
        scrollbar = Scrollbar(frame_docstr, command=text_docstr.yview)
        scrollbar.grid(row=0, column=1, sticky="ns", in_=frame_docstr)
        text_docstr['yscrollcommand'] = scrollbar.set
        self.text_docstr = text_docstr

        return notebook

    def ev_treeview_select(self, ev):
        """
        <<TreeviewSelect>> event. When an item in the tree is selected, we
        update the Value view with a representation of the value that was
        selected. We also update the `Path to item` entry.
        """
        item_id = self.tree.selection()[0]
        obj = self.item_values[item_id]

        # Update Value view
        if self.show_raw_value.get() == 0:
            val_value = pprint.pformat(obj)
        else:
            val_value = obj
        self.text_value.delete(1.0, END)
        self.text_value.insert("1.0", val_value)

        # Update docstr view
        self.text_docstr.delete(1.0, END)
        self.text_docstr.insert("1.0", str(getattr(obj, '__doc__')))

        # Set "Path to entry" field value
        item_hier = []
        while item_id:
            obj = self.item_values[item_id]
            obj_name = self.tree.item(item_id)['text']
            obj_type = type(obj).__name__
            item_hier.insert(0, (obj_name, obj_type))
            item_id = self.tree.parent(item_id)

        accessor_path = "root"
        parent_type = type(self.obj).__name__
        for obj_name, obj_type in item_hier:
            if parent_type in ('list', 'set', 'tuple'):
                accessor_path += '[{}]'.format(obj_name)
            elif parent_type == 'dict':
                accessor_path += '["{}"]'.format(obj_name)
            else:
                accessor_path += '.{}'.format(obj_name)
            parent_type = obj_type
        self.accessor.delete(0, END)
        self.accessor.insert(0, accessor_path)


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

        if self.show_magic.get() == 0 and obj_name.startswith("__"):
            return

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
    elif not sys.stdin.isatty():
        contents = sys.stdin.read()
    else:
        sys.stderr.write("Usage: {} <file>\n".format(sys.argv[0]))
        sys.exit(1)

    decoded = None
    errs = []

    if not decoded:
        try:
            decoded = pickle.loads(contents)
        except Exception as e:
            errs.append( ('pickle', str(e)) )
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
