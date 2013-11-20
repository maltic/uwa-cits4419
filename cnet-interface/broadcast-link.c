/* this file handles data link layer functions, including:
 *  - CSMA/CA with binary exponential backoff
 *  - buffers and retries data to be sent
 *  - passes received data frames to the appropriate handlers
 *  - manages address resolution and maintains an address resolution cache
 */
#include "cnet-interface.h"

#define SEND_WAIT 100

/*
 * Struct for a frame
 */
typedef struct
{
        FRAMEHEADER h;
        char            msg[MAX_FRAME_SIZE];
} FRAME;



#define FRAME_SIZE(f)      (FRAME_HEADER_SIZE + f.h.len)


QUEUE frame_queue;

void link_send_data(void* data, int len)
{
	//just enqueue for now
	FRAME f;
	f.h.len = len;
	f.h.checksum = 0;
	size_t framelen;
	if(data != NULL)
        {
                memcpy(f.msg, data, len);
                framelen = FRAME_HEADER_SIZE + len;
        }
        else  
        {
                f.h.len = 0;
                framelen = FRAME_HEADER_SIZE;
        }
        f.h.checksum  = CNET_crc32((unsigned char *)&f, (int)framelen);
	queue_add(frame_queue,&f,sizeof(f));
	CNET_start_timer(EV_LINK_SEND, SEND_WAIT, 0);
}

void reset_send_timer()
{
        if(queue_nitems(frame_queue) > 0)
        {
                CNET_start_timer(EV_LINK_SEND, SEND_WAIT, 0);
        }
}

static EVENT_HANDLER(send_timer)
{
	if(CNET_carrier_sense(1)==0)
        {
                if(queue_nitems(frame_queue) > 0)
                {
			size_t len;
                        FRAME* f = queue_remove(frame_queue,&len);
			size_t framelen = FRAME_HEADER_SIZE + f->h.len;
                        CHECK(CNET_write_physical_reliable(1, f, &framelen));
                }
        }
	reset_send_timer();
}

static EVENT_HANDLER(receive)
{
	FRAME f;
	size_t len;
	int link;
	uint32_t checksum;
	len = MAX_FRAME_SIZE;
	CHECK(CNET_read_physical(&link, &f, &len));
	       
	checksum    = f.h.checksum;
        f.h.checksum  = 0;
	uint32_t new_check = CNET_crc32((unsigned char *)&f, len);
	if(new_check != checksum) {
		return;
	}

	net_recv(f.msg,f.h.len);
}

/*
 * called on program initialisation
 * */
void link_init()
{
        /* set mac address */
        /* register CNET handlers for physical ready */
        CHECK(CNET_set_handler(EV_PHYSICALREADY, receive, 0));
	CHECK(CNET_set_handler(EV_LINK_SEND, send_timer,0));
        frame_queue = queue_new();
	printf("%d: Finished link_init()\n",nodeinfo.address);
}
