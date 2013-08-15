package model;

import java.util.ArrayList;

public abstract class NetworkLayer {
	protected int id;
	private static int nextId = 1;
	private ArrayList<Packet> inbox;
	public NetworkLayer() {
		this.id = nextId++;
		this.inbox = new ArrayList<Packet>();
	}
	public abstract void broadcast(Packet msg);
	public void recieve(Packet msg) {
		this.inbox.add(msg);
	}
	public Packet[] popInbox() {
		Packet[] tmp = (Packet[]) inbox.toArray();
		inbox.clear();
		return tmp;
	}
}
