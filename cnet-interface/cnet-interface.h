#include "../cnet/cnet.h"
#include "../cnet/cnetsupport.h"
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>
#include <assert.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <fcntl.h>
#include <unistd.h>
#include <stdio.h>
#include <errno.h>


typedef struct
{
        size_t          len;
        uint32_t        checksum;
} FRAMEHEADER;

typedef struct
{
	int len;
	CnetAddr dest; //this is just an integer
} MSGHEADER;


#define MAX_FRAME_SIZE WLAN_MAXDATA /* TODO: What is this actually? All other max sizes are based on this. */

#define FRAME_HEADER_SIZE sizeof(FRAMEHEADER)
#define MSG_HEADER_SIZE sizeof(MSGHEADER)
//#define MAX_MESSAGE_SIZE (MAX_FRAME_SIZE - FRAME_HEADER_SIZE)
//set to frame size so we don't have to bother with a transport layer

#define PIPE_MSG_SIZE 100

/*TIMERS*/
#define EV_LINK_SEND EV_TIMER1
#define EV_DO_ROUTING EV_TIMER2
#define EV_WALKING EV_TIMER9

/* broadcast-link.c */
void link_send_data( void * msg, int len);
void link_init();

/* dummy-net.c */
void net_recv( void * msg, int len);
void net_init();

/* walking.c */
void get_rand_pos(CnetPosition *new, CnetPosition max);
void walking_init();
