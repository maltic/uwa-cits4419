package implementation;
import model.*;
import model.ApplicationLayer.RouteRequest;

public class DSR extends Protocol {
	public DSR(NetworkLayer nl, ApplicationLayer al) {
		super(nl, al);
	}
	@Override
	public void update() {
		Packet[] recievedPackets = this.netLayer.popInbox();
		//do something with all the packets I just received
		
		RouteRequest[] toSend = this.appLayer.popRouteReqs();
		//do something with all the requests to route packets around
		
		// TODO Auto-generated method stub
		
	}
}
