package model;

import java.util.ArrayList;


public abstract class ApplicationLayer {
	
	public class RouteRequest {
		public Packet msg;
		public int toId;
		public RouteRequest(Packet m, int to) {
			this.msg = m;
			this.toId = to;
		}
	}
	
	protected Protocol prot;
	private ArrayList<RouteRequest> routes;
	
	public ApplicationLayer(Protocol p) {
		this.prot = p;
		routes = new ArrayList<RouteRequest>();
	}
	public abstract void accept(Packet msg);
	public RouteRequest[] popRouteReqs() {
		RouteRequest[] tmp = (RouteRequest[]) routes.toArray();
		routes.clear();
		return tmp;
	}
	public void pushRoutReq(Packet msg, int to) {
		routes.add(new RouteRequest(msg, to));
	}
	
}
