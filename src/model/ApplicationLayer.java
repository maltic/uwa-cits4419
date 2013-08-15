package model;
public abstract class ApplicationLayer {
	protected Protocol prot;
	public ApplicationLayer(Protocol p) {
		this.prot = p;
	}
	public abstract void accept(Packet msg);
}
