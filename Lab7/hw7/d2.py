from kazoo.recipe.watchers import ChildrenWatch
from kazoo.client import KazooClient
import time
from threading import Thread
import sys
from treelib import Node, Tree
from tkinter import *
from tkinter import ttk


zk: KazooClient = None
a_created = False
new_empty = {}
gui = None


class GuiThread(Thread):

    def __init__(self):
        Thread.__init__(self)

    def update(self, number: int, tree: Tree, start: str):
        self.root.after(0, self.__sub_update, number, tree, start)

    def __sub_update(self, number: int, tree: Tree, start: str):
        self.label.config(text=str(number))
        self.tree.delete(*self.tree.get_children())
        view_id = self.tree.insert("", END, text=start[1:])
        for c in tree.children(start):
            c: Node
            subtree = tree.subtree(c.identifier)
            self.__update_tree(subtree, c.identifier, view_id)
        self.__expand_tree(self.tree, "")

    def __update_tree(self, tree: Tree, node_id: str, parent: str):
        view_id = self.tree.insert(parent, END, text=tree[node_id].tag)
        for c in tree.children(node_id):
            subtree = tree.subtree(c.identifier)
            self.__update_tree(subtree, c.identifier, view_id)

    def __expand_tree(self, tree: ttk.Treeview, item: str):
        children = tree.get_children(item)
        for child in children:
            tree.item(child, open=True)
            self.__expand_tree(tree, child)

    def run(self):
        self.root = Tk()
        self.root.title("Znodes")
        self.root.protocol("WM_DELETE_WINDOW", lambda: None)
        self.frm = ttk.Frame(self.root, width=600, height=600)
        self.frm.grid(row=0, column=0, sticky="NW")

        self.root.resizable(False, False)
        self.label: ttk.Label = ttk.Label(
            self.frm, text="0",font='Arial 17 bold')
        self.tree: ttk.Treeview = ttk.Treeview(self.frm)
        tmp_label = ttk.Label = ttk.Label(
            self.frm, text="Liczba potomków:",font='Arial 17 bold')
        tmp_label.place(relx=0.5, rely=0.15, anchor=CENTER)
        self.label.place(relx=0.5, rely=0.2, anchor=CENTER)
        self.tree.place(relx=0.5, rely=0.5, anchor=CENTER,width=500)
        print(self.label)
        self.hide()
        self.root.mainloop()

    def show(self):
        self.root.after(0, self.root.deiconify)

    def hide(self):
        self.root.after(0, self.root.withdraw)


gui: GuiThread


def run_gui():
    global gui
    gui.show()


def stop_gui():
    global gui
    gui.hide()


def update_gui(number: int, tree: Tree, start: str):
    gui.update(number, tree, start)


def get_tree_size(path):
    global zk
    res = 1
    for c in zk.get_children(path):
        res += get_tree_size(f"{path}/{c}")
    return res


def generate_tree(path: str):
    global zk
    tree = Tree()
    tree.create_node(path.split("/")[-1], path)
    for c in zk.get_children(path):
        sub_generate_tree(f"{path}/{c}", tree, path)
    return tree


def sub_generate_tree(path: str, tree: Tree, parent: str):
    tree.create_node(path.split("/")[-1], path, parent)
    for c in zk.get_children(path):
        sub_generate_tree(f"{path}/{c}", tree, path)


def a_trigger(children, name):
    global a_created
    if 'a' in children and not a_created:
        run_gui()
        a_created = True
        ws = f"/a"
        zk.ChildrenWatch(
            ws, func=lambda ch: b_trigger(ch, ws))
        tree = generate_tree("/a")
        size = get_tree_size("/a")-1
        print(tree)
        update_gui(size, tree, "/a")
    else:
        a_created = False
        stop_gui()


def b_trigger(children, path):
    for c in children:
        new_empty.update({path: False})
        ws = f"{path}/{c}"
        new_empty.update({ws: True})
        zk.ChildrenWatch(
            ws, func=lambda ch: b_trigger(ch, ws))

    if not new_empty.get(path):
        tree = generate_tree("/a")
        size = get_tree_size("/a")-1
        print(tree)
        update_gui(size, tree, "/a")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        addres = None
    else:
        addres = sys.argv[1]
    zk = KazooClient(addres)
    zk.start()
    gui = GuiThread()
    gui.start()
    zk.ChildrenWatch("/", func=lambda d: a_trigger(d, "/"))
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    zk.stop()
