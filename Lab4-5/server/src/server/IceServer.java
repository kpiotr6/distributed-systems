package server;

import com.zeroc.Ice.Communicator;
import com.zeroc.Ice.Identity;
import com.zeroc.Ice.ObjectAdapter;
import com.zeroc.Ice.Util;

import java.util.logging.Level;
import java.util.logging.Logger;

public class IceServer {
	private static final Logger LOGGER = Logger.getLogger( IceServer.class.getName() );
	public void t1(String[] args) {
		int status = 0;
		Communicator communicator = null;
		try {
			communicator = Util.initialize(args,"config.server");
			ObjectAdapter adapter = communicator.createObjectAdapter("Adapter1");
			ServantEvictor e = new ServantEvictor(2);
			ObjectManagerI destroyer = new ObjectManagerI(e);
			adapter.add(destroyer,new Identity("destroyer","all"));
			adapter.addServantLocator(e,"multiple");
			adapter.addDefaultServant(new SortDefaultI(),"single");
			adapter.activate();
			System.out.println("Entering event processing loop...");
			communicator.waitForShutdown();

		} catch (Exception e) {
			LOGGER.log(Level.SEVERE, e.toString(), e);
			status = 1;
		}
		if (communicator != null) {
			try {
				communicator.destroy();
			} catch (Exception e) {
				LOGGER.log(Level.SEVERE, e.toString(), e);
				status = 1;
			}
		}
		System.exit(status);
	}


	public static void main(String[] args) {
		IceServer app = new IceServer();
		app.t1(args);
	}
}