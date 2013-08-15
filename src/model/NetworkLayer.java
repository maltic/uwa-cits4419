package model;
public abstract class NetworkLayer {
	protected int id;
	private static int nextId = 1;
	public NetworkLayer() {
		this.id = nextId++;
	}
	public abstract void broadcast(Packet msg);
	public abstract void recieve(Packet msg);
}
