from kazoo.recipe.watchers import ChildrenWatch
from kazoo.client import KazooClient
import time
import sys
import tkinter as tk
from tkinter import ttk
from threading import Thread
import queue
app = None
nodes_label = None
graph = None
var = None
zk = KazooClient("127.0.0.1:2181")

def create_interface():
    global app
    global nodes_label
    global graph
    global var
    app = tk.Tk()
    frm = ttk.Frame(app, padding=10)
    frm.grid()
    var = tk.StringVar()
    nodes_label = ttk.Label(frm, textvariable=var).grid(column=0, row=0)
    graph = ttk.Treeview(frm).grid(column=1, row=0)
    app.mainloop()
    app.destroy()
    app = None


def traverse(path):
    global zk
    res = 0
    for c in zk.get_children(path):
        res += traverse(f"path/{c}")
    return res


def a_trigger(children):
    global app
    global nodes_label
    print(children)
    for c in children:
        print("ssssss")
        ChildrenWatch(zk, f"/a/{c}")(lambda x: a_descendants_trigger(x))
    if 'a' in children and app is None:
        # Thread(target=create_interface).start()
        pass
    # elif 'a' not in children and app is not None:
    #     app.quit()
    



def a_descendants_trigger(children):
    global app
    print("f")
    print(traverse("/a"))
    pass

if __name__ == "__main__":
    zk.start()
    a_watcher = ChildrenWatch(zk, "/", func=a_trigger)
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    zk.stop()