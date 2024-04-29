package server;

import com.zeroc.Ice.Current;
import sorting.Ordering;

import java.util.Comparator;
import java.util.List;

public class BubbleSort extends AbstractSort{
    @Override
    public void sortList(Ordering ordering, Current current) {
        Long tmp;
        List<Long> s = this.seqList;
        Comparator<Long> cmp;
        if (ordering.equals(Ordering.ASCENDING)){
            cmp = Long::compareTo;
        }
        else {
            cmp = Comparator.reverseOrder();
        }
        boolean swapped;
        for (int i = 0; i < s.size() - 1; i++) {
            swapped = false;
            for (int j = 0; j < s.size() - i - 1; j++) {
                if (cmp.compare(s.get(j),s.get(j+1))>0) {
                    tmp = s.get(j);
                    s.set(j, s.get(j + 1));
                    s.set(j + 1,tmp);
                    swapped = true;
                }
            }
            if (!swapped)
                break;
        }

    }
}
