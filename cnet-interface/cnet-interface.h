#include <cnet.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>
#include <assert.h>




typedef struct
{
        size_t          len;
        uint32_t        checksum;
} FRAMEHEADER;


#define MAX_FRAME_SIZE WLAN_MAXDATA /* TODO: What is this actually? All other max sizes are based on this. */

#define FRAME_HEADER_SIZE sizeof(FRAMEHEADER)
#define MAX_MESSAGE_SIZE (MAX_FRAME_SIZE - FRAME_HEADER_SIZE)

/* broadcast-link.c */
void link_send_data( char * msg, int len);
void link_init();

/* dummy-net.c */
void net_recv( char * msg, int len);
void net_init();


