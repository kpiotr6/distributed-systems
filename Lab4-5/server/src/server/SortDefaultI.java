package server;

import com.zeroc.Ice.Current;
import com.zeroc.Ice.ObjectNotExistException;
import sorting.Ordering;
import sorting.SortDefault;

import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;
import java.util.logging.Level;
import java.util.logging.Logger;

public class SortDefaultI implements SortDefault {

    private static final Logger LOGGER = Logger.getLogger( SortDefaultI.class.getName());
    public SortDefaultI() {
        LOGGER.log(Level.INFO, "{0} created", this.getClass().getName());
    }

    @Override
    public List<Long> sortList(Ordering ordering, List<Long> toSort, Current current) {
        switch (ordering){
            case ASCENDING -> toSort.sort(Long::compareTo);
            case DESCENDING -> toSort.sort(Comparator.reverseOrder());
        }
        return toSort;
    }

}
