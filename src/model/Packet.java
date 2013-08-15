package model;
public class Packet {
	private String header;
	private String contents;
	private int senderId;
	public Packet(String head, String cont, int sid) {
		this.contents = cont;
		this.header = head;
		this.senderId = sid;
	}
	public String getContents() {
		return this.contents;
	}
	public String getHeader() {
		return this.header;
	}
	public int getSenderId() {
		return this.senderId;
	}  
}
