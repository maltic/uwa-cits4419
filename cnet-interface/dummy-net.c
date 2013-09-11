#include "cnet-interface.h"


//TODO This probably needs tweaking
#define ROUTETIME 100

QUEUE unrouted;
QUEUE routed;

typedef struct
{
	char msg[MAX_MESSAGE_SIZE];
	int len;
} MSG;


EVENT_HANDLER(app_rdy)
{
	MSG data;
	CNET_read_application(data.msg,&(data.len));
	queue_add(unrouted, data, sizeof(data));
}

EVENT_HANDLER(get_routed_messages)
{
	//send messages that need routing

	//get routed messages
		
	//then push everything down to the link layer
	while(queue_nitems(routed) > 0) {
		MSG *next;
		size_t len;
		next = queue_remove(routed,&len);
		link_send_data(next.msg,next.len);
		free(next);
	}
}

void net_recv(char * msg, int len)
{
	//enqueue for routing
	MSG m;
	m.msg = msg;
	m.len = len;
	queue_add(unrouted,&m,sizeof(m));
}

void net_init()
{
	unrouted = queue_new();
	routed = queue_new();	
	CNET_set_handler(EV_APPLICATIONREADY, app_rdy, 0)
	CNET_set_handler(EV_TIMER1,get_routed_messages,0)
	CNET_start_timer(EV_TIMER1, ROUTETIME, 1);
}
