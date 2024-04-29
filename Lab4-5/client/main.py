import sys, Ice
import os
from CommandEnum import CommandEnum
sys.path.append(os.path.join(os.path.dirname(__file__), 'generated'))
import sorting
import traceback

all_proxies = dict()
communicator = Ice.initialize(sys.argv)
destroyer = communicator.stringToProxy("all/destroyer:tcp -h 127.0.0.2 -p 10000 -z")
destroyer: sorting.ObjectManagerPrx = sorting.ObjectManagerPrx.checkedCast(destroyer)


def parse(command_value: str):
    command_parts = command_value.split(" ")
    command_string = CommandEnum[command_parts[0].upper()]

    if command_string == CommandEnum.LIST:
        return command_string, None
    if len(command_parts) < 2:
        raise Exception("Command too short")
    cat_name = command_parts[1]
    cat = cat_name.split("/")[0]
    if cat != "multiple" and cat != "single":
        raise Exception("Category not existent")

    match command_string:
        case CommandEnum.SORT:
            if len(command_parts) < 4:
                raise Exception("SORT command too short")
            l = list(map(lambda x: int(x),command_parts[2].split(",")))
            return command_string, cat_name, l,  command_parts[3]
        case CommandEnum.CREATE:
            if len(command_parts) < 3:
                raise Exception("CREATE command too short")
            return command_string, cat_name, command_parts[2]
        case CommandEnum.DESTROY:
            return command_string, cat_name


def execute(command: CommandEnum, cat_name: str, c2=None, c3=None):
    match command:
        case CommandEnum.CREATE:
            if all_proxies.get(cat_name) is not None:
                raise Exception("Proxy for this object exists")
            prx = communicator.stringToProxy(cat_name+":tcp -h 127.0.0.2 -p 10000 -z")
            all_proxies.update({cat_name: prx})

        case CommandEnum.SORT:
            prx = all_proxies.get(cat_name)
            if prx is None:
                raise Exception("Proxy non existent")
            if c3 == "A":
                ordering = sorting.Ordering.ASCENDING
            elif c3 == "D":
                ordering = sorting.Ordering.DESCENDING
            else:
                raise Exception("No such ordering")
            if cat_name.split("/")[0] == "multiple":
                prx: sorting.SortPrx = sorting.SortPrx.uncheckedCast(prx)
                prx.setList(c2)
                prx.sortList(ordering)
                return prx.getList()
            if cat_name.split("/")[0] == "single":
                prx: sorting.SortDefaultPrx = sorting.SortDefaultPrx.uncheckedCast(prx)
                return prx.sortList(ordering, c2)

        case CommandEnum.LIST:
            for k, v in all_proxies.items():
                print(k)
            print("Remote:")
            for s in destroyer.listObjects():
                print(s)

        case CommandEnum.DESTROY:
            prx = all_proxies.get(cat_name)
            if prx is None:
                raise Exception("Proxy non existent")
            cat,name = cat_name.split("/")
            destroyer.destroy(cat,name)
            all_proxies.pop(cat_name)









if __name__ == "__main__":

    while True:
        try:
            command = input(">>>")
            res = parse(command)
            serv = execute(*res)
            if serv is not None:
                print(serv)
        except KeyboardInterrupt:
            communicator.destroy()
            exit(0)
        except Ice.LocalException as e:
            print(e)
        except Exception as e:
            print(e)


    with Ice.initialize(sys.argv) as communicator:
        s1 = communicator.stringToProxy("multiple/s1:tcp -h 127.0.0.2 -p 10000 -z")
        context = dict()
        context.update({"sort-type": "bubble"})
        # s1 = s1.ice_context(context)
        s1:SortPrx = SortPrx.checkedCast(s1)
        s1.setList([123,2,3,1],context)
        print(s1.getList())
        # s1 = communicator.stringToProxy("single/s2:tcp -h 127.0.0.2 -p 10000 -z")
        # context = dict()
        # context.update({"sort-type": "bubble"})
        # s1 = s1.ice_context(context)
        # s1:SortDefaultPrx = SortDefaultPrx.uncheckedCast(s1)
        # print(s1.sortList(Ordering.DESCENDING,[2,44,1,55]))
        # s1:SortPrx = SortPrx.checkedCast(s1)
        #
        # s1.setList([2,1,55])
        # s1.setList([2, 1, 22])
        # # s1.sortList(Ordering.ASCENDING)
        # print(s1.getList()
