package server;


import com.zeroc.Ice.Current;
import sorting.Ordering;
import sorting.Sort;

import java.util.List;

public abstract class AbstractSort implements Sort {
    protected List<Long> seqList;
    @Override
    public void setList(List<Long> seq, Current current) {
        this.seqList = seq;
    }

    @Override
    public List<Long> getList(Current current) {
        return this.seqList;
    }
    @Override
    public abstract void sortList(Ordering ordering, Current current);

}
