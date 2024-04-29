package server;

import com.zeroc.Ice.Current;
import com.zeroc.Ice.Identity;
import sorting.ObjectManager;

import java.util.List;
import java.util.logging.Level;
import java.util.logging.Logger;

public class ObjectManagerI implements ObjectManager {
    private static final Logger LOGGER = Logger.getLogger( ObjectManagerI.class.getName());
    private ServantEvictor evictor;

    public ObjectManagerI(ServantEvictor evictor) {
        this.evictor = evictor;
    }

    @Override
    public List<String> listObjects(Current current) {
        LOGGER.log(Level.INFO,"List objects");
        return evictor.getObjectsIdentities();
    }

    @Override
    public void destroy(String category, String name, Current current) {
        Identity id = new Identity(name,category);
        if (current.adapter.find(id)!=null){
            current.adapter.remove(id);
            LOGGER.log(Level.INFO, "Object removed {0}\\{1}",new Object[]{category,name});
        }
        else {
            evictor.removeServant(id);
            LOGGER.log(Level.INFO, "Object removed {0}\\{1}",new Object[]{category,name});
        }

    }
}
