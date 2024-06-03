from kazoo.recipe.watchers import ChildrenWatch
from kazoo.client import KazooClient
import time
import sys
import tkinter as tk
from tkinter import ttk
from threading import Thread
import queue

zk = KazooClient("127.0.0.1:2181")
watchers = []


def traverse(path):
    global zk
    res = 0
    for c in zk.get_children(path):
        res += traverse(f"path/{c}")
    return res


def a_trigger(children, name):
    print(children)
    print(name)
    # watchers.append(zk.ChildrenWatch(name, func=b_trigger))
    # for c in zk.get_children(name):
    #     watchers.append(zk.ChildrenWatch(f"{name}/{c}",func=b_trigger))
    # pass
    # print(children)
    # watchers.append(zk.ChildrenWatch(f"/a",func=b_trigger))
    # for c in children:
    #     watchers.append(zk.ChildrenWatch(f"/a/{c}",func=b_trigger))
    # pass


def b_trigger(children):
    # print("lol")
    # print(children)
    # for c in children:
    #     watchers.append(zk.ChildrenWatch(f"/a/{c}", func=b_trigger))
    pass


if __name__ == "__main__":
    zk.start()
    a_watcher = zk.ChildrenWatch("/a", func=lambda d: a_trigger(d, "/a"))
    # watchers.append(zk.ChildrenWatch(f"/a/a",func=b_trigger))
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    zk.stop()
