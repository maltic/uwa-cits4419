UDP Proof of Concept Protocol Secification

Message: is a string sent between nodes via a UDP socket.

	DSR Message: Starts with the characters 'dsr'
		Route-Request Message: 'dsr-rreq-.....'
		Route-Reply   Message: 'dsr-rrpy......'
		Route-Error   Message: 'dsr-err.......'

#someone else define the rest of the data structures for the rest of the messages.


	Data message: Starts with a '#' character followed by the message.

