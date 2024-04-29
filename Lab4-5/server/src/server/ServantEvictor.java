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
    private final Set<String> removed;
    private final int size;
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
        List<String> all = new ArrayList<>(queue.stream().toList());
        all.addAll(removed);
        return all;
    }
    public void removeServant(Identity identity){
        String catName = identity.category+"/"+identity.name;
        if(queue.contains(catName)){
            queue.remove(catName);
            map.remove(catName);
        }
        if(removed.contains(catName)){
            removed.remove(catName);
            ObjectSaver.remove(catName);
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

        if (entry != null) {
            queue.remove(catName);
        } else if(removed.contains(catName)) {
            entry = new EvictorEntry();
            entry.servant = loadServant(catName);
            entry.useCount = 0;
            map.put(catName, entry);
            evictServants();
        } else {
            entry = new EvictorEntry();
            entry.servant = createServant(current);
            entry.useCount = 0;
            map.put(catName, entry);
            evictServants();
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
    private Object loadServant(String filename){

        Object o = (Object) ObjectSaver.read(filename);
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