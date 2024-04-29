package server;

import com.zeroc.Ice.Current;
import com.zeroc.Ice.Identity;
import com.zeroc.Ice.Object;
import com.zeroc.Ice.ServantLocator;
import sorting.Sort;

import java.util.*;
import java.util.logging.Level;
import java.util.logging.Logger;

public class ServantEvictor implements ServantLocator
{
    private static final Logger LOGGER = Logger.getLogger( ServantEvictor.class.getName());
    private final java.util.Map<String, EvictorEntry> map;
    private final List<String> queue;


    private class EvictorEntry
    {
        Object servant;

        int useCount;
    }

    public ServantEvictor(int size) {
        this.map = new java.util.HashMap<>();
        this.queue = new LinkedList<>();
    }
    public List<String> getObjectsIdentities(){
        return queue;
    }
    public void removeServant(Identity identity){
        String catName = identity.category+"/"+identity.name;
        if(queue.contains(catName)){
            queue.remove(catName);
            map.remove(catName);
        }
    }
    public AbstractSort createServant(Current current){
        Map<String, String> ctx = current.ctx;
        String sortType = ctx.get("sort-type");
        if(sortType == null){
            sortType = "bubble";
        }

        AbstractSort sort = switch (sortType) {
            case "insertion" -> new InsertionSort();
            case "bubble" -> new BubbleSort();
            default -> new BubbleSort();
        };

        LOGGER.log(Level.INFO, "New servant created {0}",sort.getClass().getName());
        return sort;
    }

    public LocateResult locate(com.zeroc.Ice.Current current)
    {
        LOGGER.log(Level.INFO, "Servant locator locate method");
        String catName = current.id.category+"/"+current.id.name;
        EvictorEntry entry = map.get(catName);

        if (entry == null) {
            entry = new EvictorEntry();
            entry.servant = createServant(current);

            entry.useCount = 0;
            queue.add(0,catName);
            map.put(catName, entry);

        }
        ++(entry.useCount);
        return new LocateResult(entry.servant, entry);
    }


    public void finished(com.zeroc.Ice.Current current, com.zeroc.Ice.Object servant, java.lang.Object cookie)
    {
        ((EvictorEntry)cookie).useCount--;

    }

    public void deactivate(String category)
    {

    }

}