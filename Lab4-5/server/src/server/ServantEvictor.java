package server;

import com.zeroc.Ice.Current;
import com.zeroc.Ice.Identity;
import com.zeroc.Ice.Object;
import com.zeroc.Ice.ServantLocator;
import sorting.Sort;

import java.util.*;
import java.util.logging.Level;
import java.util.logging.Logger;

public class ServantEvictor implements ServantLocator, ObjectMapper
{
    private static final Logger LOGGER = Logger.getLogger( ServantEvictor.class.getName());
    private final java.util.Map<Identity, EvictorEntry> map;
    private final List<String> queue;
    private final Set<String> removed;
    private int size;
    private class EvictorEntry
    {
        Object servant;

        int useCount;
    }

    public ServantEvictor(int size) {
        this.size = size;
        this.map = new java.util.HashMap<>();
        this.queue = new LinkedList<>();
        this.removed = new HashSet<>();
    }
    public List<String> getObjectsIdentities(){
        return queue;
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

        EvictorEntry entry = map.get(current.id);
        String catName = current.id.category+"/"+current.id.name;
        if (entry != null) {
            queue.remove(catName);
        } else if(removed.contains(catName)) {
            map.put(new Identity()loadServant(catName);
            evictServants();
        } else {
            entry = new EvictorEntry();
            entry.servant = createServant(current);
            entry.useCount = 0;
            map.put(current.id, entry);
        }
        ++(entry.useCount);
        queue.add(0,catName);
        return new LocateResult(entry.servant, entry);
    }
    private void evictServants()
    {

        while(this.size<queue.size()){
            String name = queue.get(this.size+1);
            queue.remove(name);
            ObjectSaver.save(this.map.get(name),name);
            removed.add(name);
        }
    }
    private java.lang.Object loadServant(String filename){
        java.lang.Object o = ObjectSaver.read(filename);
        removed.remove(filename);
        queue.add(0,filename);
        return o;

    }

    public void finished(com.zeroc.Ice.Current current, com.zeroc.Ice.Object servant, java.lang.Object cookie)
    {
        ((EvictorEntry)cookie).useCount--;

    }

    public void deactivate(String category)
    {
        for(String r: removed){
            ObjectSaver.remove(r);
        }
    }

}