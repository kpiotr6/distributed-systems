from kazoo.recipe.watchers import ChildrenWatch
from kazoo.client import KazooClient
import time
from threading import Thread

from treelib import Node, Tree
from tkinter import *
from tkinter import ttk


zk = KazooClient("127.0.0.1:2181")
watchers = []
a_created = False
new_empty = {}
gui = None


class Gui:

    def __init__(self):
        Thread.__init__(self)
        self.root = Tk()
        self.frm = ttk.Frame(self.root, padding=10)
        self.label: ttk.Label = ttk.Label(
            self.frm, text="Hello World!").grid(column=0, row=0)
        self.tree: ttk.Treeview = ttk.Treeview(self.frm).grid(column=1, row=0)
        self.stopped = False
        self.frm.grid()

    def update(self, number: int, tree: Tree, start: str):
        self.root.after(100, self.update, number, tree, start)

    def sub_update(self, number: int, tree: Tree, start: str):
        self.label.config(text=str(number))
        self.tree.delete(*self.tree.get_children())
        self.tree.insert("", END, start)
        for c in tree.children(start):
            c: Node
            subtree = tree.subtree(c.identifier)
            self.update_tree(subtree, c.identifier, start)

    def update_tree(self, tree: Tree, node_id: str, parent: str):
        self.tree.insert(parent, END, node_id)
        for c in tree.children(node_id):
            c: Node
            subtree = tree.subtree(c.identifier)
            self.update_tree(subtree, c.identifier)

    def run(self):
        self.root.mainloop()

    def stop(self):
        self.stopped = True
        if self.stopped:
            self.root.after(100, self.root.destroy)
            return


def run_gui():
    gui = Gui()
    gui.run()


def stop_gui():
    global gui
    gui.stop()


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
    run_gui()
    global a_created
    if 'a' in children and not a_created:
        ws = f"/a"
        watchers.append(ws)
        zk.ChildrenWatch(
            ws, func=lambda ch: b_trigger(ch, ws))
        a_created = True
        print("/a")
        tree = generate_tree("/a")
        size = get_tree_size("/a")-1
        print(tree)
        update_gui(size, tree, "/a")
    else:
        a_created = False


def b_trigger(children, path):
    for c in children:
        new_empty.update({path: False})
        ws = f"{path}/{c}"
        new_empty.update({ws: True})
        watchers.append(ws)
        zk.ChildrenWatch(
            ws, func=lambda ch: b_trigger(ch, ws))

    if not new_empty.get(path):
        print("/a")
        tree = generate_tree("/a")
        size = get_tree_size("/a")-1
        print(tree)
        update_gui(size, tree, "/a")


if __name__ == "__main__":
    zk.start()
    watchers.append("/")
    zk.ChildrenWatch("/", func=lambda d: a_trigger(d, "/"))
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    zk.stop()
