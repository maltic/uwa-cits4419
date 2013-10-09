#include "cnet-interface.h"


//TODO This probably needs tweaking
#define ROUTETIME 5000

QUEUE unrouted;
QUEUE routed;

typedef struct
{
	MSGHEADER h;
	char msg[MAX_MESSAGE_SIZE];

} MSG;


EVENT_HANDLER(app_rdy)
{
	char msg[MAX_MESSAGE_SIZE];
        int dest;
        size_t len = MAX_MESSAGE_SIZE;
        CHECK(CNET_read_application(&dest, &msg, &len));
	//should pass off to a transport layer here
	MSG m;
	m.h.hops = 0;
	m.h.len = len;
	m.h.dest = dest;
	memcpy(m.msg,msg,len);
	len = len + MSG_HEADER_SIZE;
	queue_add(unrouted, &m, len);
}

EVENT_HANDLER(get_routed_messages)
{
	//ROUTING WILL HAPPEN IN HERE SOMEHWERE

	//send messages that need routing to routing layer
	//QUEUE to_route = queue_new();
	while(queue_nitems(unrouted) > 0) {
		size_t len;
		MSG* m = queue_remove(unrouted,&len);
		printf("Node %d: Message for %d\n",nodeinfo.address,m->h.dest);
		if(m->h.dest == nodeinfo.address) 
		{	
			printf("Node %d: receiving message\n");
			size_t len = m->h.len;
			CHECK(CNET_write_application(m->msg,&len));
		}
		else
		{
			printf("Node %d: passing message away\n");
			if(m->h.hops < MAXHOPS) {
				m->h.hops++;
				queue_add(routed,m,len); //needs to be changed to to_route eventually;
			}
		}
	}
	//push everything down everything in to_route to routing layer
	//for now we just don't route them, we just flood one hop

	//get routed messages
		
	//then push everything down to the link layer
	while(queue_nitems(routed) > 0) {
		MSG *next;
		size_t len;
		next = queue_remove(routed,&len);
		link_send_data(next,len);
		//free(next);
	}
	CNET_start_timer(EV_DO_ROUTING, ROUTETIME, 1);
}

void net_recv(void* msg, int len)
{
	//enqueue for routing
	queue_add(unrouted,msg,len);
}

void net_init()
{
	unrouted = queue_new();
	routed = queue_new();
	CNET_set_handler(EV_APPLICATIONREADY, app_rdy, 0);
	CNET_set_handler(EV_DO_ROUTING,get_routed_messages,0);
	CNET_start_timer(EV_DO_ROUTING, ROUTETIME, 1);
}

EVENT_HANDLER(reboot_node)
{
	link_init();
	net_init();
	walking_init();
	CHECK(CNET_enable_application(ALLNODES));
}

