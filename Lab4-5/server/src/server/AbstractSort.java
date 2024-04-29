package server;


import com.zeroc.Ice.Current;
import sorting.Ordering;
import sorting.Sort;

import java.util.List;
import java.util.logging.Level;
import java.util.logging.Logger;

public abstract class AbstractSort implements Sort {
    private static final Logger LOGGER = Logger.getLogger( AbstractSort.class.getName());
    protected List<Long> seqList;
    @Override
    public void setList(List<Long> seq, Current current) {
        LOGGER.log(Level.INFO, "Set List");
        this.seqList = seq;
    }

    @Override
    public List<Long> getList(Current current) {
        LOGGER.log(Level.INFO, "Get List");
        return this.seqList;
    }
    @Override
    public abstract void sortList(Ordering ordering, Current current);

}
