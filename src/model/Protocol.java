package model;

public abstract class Protocol {
	protected NetworkLayer netLayer;
	protected ApplicationLayer appLayer;
	public Protocol(NetworkLayer nl, ApplicationLayer al) {
		this.netLayer = nl;
		this.appLayer = al;
	}
	public abstract void route(Packet p, int toId);
}
