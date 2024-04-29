package server;

import com.zeroc.Ice.Current;
import sorting.Ordering;

import java.util.Comparator;
import java.util.List;
import java.util.logging.Level;
import java.util.logging.Logger;

public class InsertionSort extends AbstractSort{
    private static final Logger LOGGER = Logger.getLogger( InsertionSort.class.getName());

    @Override
    public void sortList(Ordering ordering, Current current) {
        LOGGER.log(Level.INFO, "Sort List");
        Long tmp;
        List<Long> s = this.seqList;
        Comparator<Long> cmp;
        if (ordering.equals(Ordering.ASCENDING)){
            cmp = Long::compareTo;
        }
        else {
            cmp = Comparator.reverseOrder();
        }
        int n = s.size();
        for (int i = 1; i < n; ++i) {
            Long key = s.get(i);
            int j = i - 1;
            while (j >= 0 && cmp.compare(s.get(j),key)>0) {
                s.set(j + 1, s.get(j));
                j = j - 1;
            }
            s.set(j + 1, key);
        }

    }
}
