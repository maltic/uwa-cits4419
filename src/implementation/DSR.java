package implementation;
import model.*;
public class DSR extends Protocol {
	public DSR(NetworkLayer nl, ApplicationLayer al) {
		super(nl, al);
	}
	public void route(Packet msg, int to) {
		return; //stub
	}
}
