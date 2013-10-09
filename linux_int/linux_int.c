//Linux Integration Daemon

// Functions:
//  - Linux Route Table Manipulation
//  - Linux Promiscuous Socket Monitoring

//Message Queues:
// ROUTE_OPS - for reciept of route add/del requests from the routing engine
// PROMISC_PKTS - for sending promiscuous packet info to routing engine
// ROUTE_REQUESTS - for sending route requests to the routing engine.
// RELEASE_PKT - for IPC between route operations and default packet thread.

//Threads:
// Main:
//	Child: Route Operations (msg recieve on ROUTE_OPTS)
//	Child: Default Packets (msg send on ROUTE_REQUESTS)
//	Child: Promisc Packets (msg send on PROMISC_PKTS)


#include <stdlib.h>
#include <stdio.h>
#include <signal.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <sys/wait.h>
#include <sys/stat.h>
#include <unistd.h>
#include <netinet/ip.h>
#include <arpa/inet.h>
#include <string.h>
#include <netinet/in.h>
#include <net/route.h>
#include <sys/ioctl.h>
#include <sys/msg.h>
#include <sys/ipc.h>
#include <pthread.h>

#define TUN_DEV_IP "127.0.0.2"	/* ip address for the tun device */
#define TUN_DEV_NAME "tun"   /* name of the tun interface */

#define MSGQ_OUT_KEY "TO_RE_Q"
#define MSGQ_IN_KEY "FROM_RE_Q"


typedef struct{
    /* 0 */ unsigned char ip_hl:4, ip_v:4;
    /* 1 */ unsigned char ip_tos;
    /* 2 */ unsigned short int ip_len;
    /* 3 */ unsigned short int ip_id;
    /* 4 */ unsigned short int ip_off;
    /* 5 */ unsigned char ip_ttl;
    /* 6 */ unsigned char ip_p;
    /* 7 */ unsigned short int ip_sum;
    /* 8 */ unsigned int ip_src;
    /* 9 */ unsigned int ip_dst;
}ipheader;

#define MSG_LENGTH 1024

typedef struct{
	long      mtype;    /* message type */
	char msgdata[MSG_LENGTH]; /* message text of length MSGSZ */
} msgbuf;


typedef struct sockaddr_in ipaddress;

// Global Variables

	//default packet FD
	int defaultFD;
	
	//promiscuous packet FD
	int rawFD;
	
//daemonize the process
void daemon_init(void)
{
    pid_t pid;
    
    struct sigaction act;
    
    if((pid = fork()) < 0)
    {
        perror("Failed to create daemon!");
    }
    else if(pid > 0)
    {
        exit(0); //don't need the parent
    }
    
    //flog("Daemon process started...\n", 0);
    
    setsid();
    umask(0);
    
    //might need some zombie prevention code here.
}


//Setup ROUTE_OPS queue and listen
void *route_operations(void *threadid)
{
	key_t key;
	int msgqid;
	size_t msgSize;
	msgbuf message;
	
	msgqid = msgget(ftok("/tmp/ROUTE_OPS", key), (IPC_CREAT | IPC_EXCL | 0666));
	
	if(msgqid < 0)
	{
		//msgsq was already created, just reference it.
		msgqid = msgget(ftok("/tmp/ROUTE_OPS", key), 0666);
		printf("route ops queue already existed");
	}
	else
	{
		printf("route ops queue created successfully");
	}
	
	while(1)
	{
		//wait for route modification messages - of any type :. 0
		msgSize = msgrcv(msgqid, &message, sizeof(msgbuf) - sizeof(long), 0, 0);
		
		//get the msg type
		if(message.mtype == 1)
		{
			//route add
			
		}
		
		if(message.mtype == 2)
		{
			//route del
		}
	}
	
	
	
	
}

//From <bits/ioctls.h>
//SIOCADDRT = 0x890B          # add routing table entry
//SIOCDELRT = 0x890C          # delete routing table entry


//add or delete routes from the linux routing table.
int route(char *dst_ip, char *mask_ip, char *gw_ip, char *operation)
{
	int rtsocket, func;
	ipaddress dst, mask, gw;
	struct rtentry route;
	
	if(strcmp(operation,"add"))
	{
		func = SIOCADDRT;
	}
	else if(strcmp(operation,"del"))
	{
		func = SIOCDELRT;
	}
	
	//make some structs to store the details in
	memset(&dst, 0, sizeof(ipaddress));
	memset(&mask, 0, sizeof(ipaddress));
	memset(&gw, 0, sizeof(ipaddress));
	
	dst.sin_family = AF_INET;
	dst.sin_family = AF_INET;
	dst.sin_family = AF_INET;
	
	rtsocket = socket(AF_INET, SOCK_DGRAM, 0);
	
	if(rtsocket < 0)
	{
		return 1;
	}
	
	dst.sin_addr.s_addr = inet_addr(dst_ip);
	mask.sin_addr.s_addr = inet_addr(mask_ip);
	gw.sin_addr.s_addr = inet_addr(gw_ip);
	
	memset(&route, 0, sizeof(struct rtentry));
	route.rt_dst = *(struct sockaddr *)&dst;
	route.rt_genmask = *(struct sockaddr *)&mask;
	route.rt_gateway = *(struct sockaddr *)&gw;
	route.rt_flags = RTF_UP | RTF_GATEWAY;
	
	if(ioctl(rtsocket, func, &route) < 0)
	{
		return 1;
	}
	else
	{
		return 0;
	}
	
	close(rtsocket);
}

int main(int argc, char **argv)
{
	char *interface;
	interface = "eth0";
	int option;
	char* iwcommand;
	struct sockaddr_in defaultRoute;
	fd_set rfdset;
	fd_set wfdset;
	char *defaultInterface;
	defaultInterface = "tap0";
	
	printf("i'm actually starting");
	
	//spin up in the background
   // daemon_init();
	
	//setup threads
	//pthread_t routeOpsThread, defaultThread, promiscThread;
	int routeOpsThreadResult, defaultThreadResult, promiscThreadResult;
	
	routeOpsThreadResult = pthread_create(&routeOpsThread, NULL, route_operations, NULL);
	//defaultThreadResult = pthread_create(&defaultThread, NULL, default_operations, NULL);
	//promiscThreadResult = pthread_create(&promiscThread, NULL, promisc_operations, NULL);
	
	if(routeOpsThreadResult)
	{
		printf("THREAD ERROR: return code for route ops: %d\n", routeOpsThreadResult);
		exit(-1);
	}

//	while(1)
//	{
//		option = getopt(argc, argv, "i:z");
//		
//		if(option == -1)
//		{
//			break;
//		}
//		
//		switch(option)
//		{
//			case 'i':
//			sprintf(interface,"%s",optarg);
//			break;
//		}
//	}
	
	//set up the required 'default' interface socket
	defaultFD = socket(AF_INET, SOCK_RAW, IPPROTO_RAW);
	setsockopt(defaultFD, SOL_SOCKET, SO_BINDTODEVICE, defaultInterface, 4);
	
	//create the raw data & promiscuous socket
	rawFD = socket(AF_INET, SOCK_RAW, IPPROTO_RAW);
	
	//bind it to our interface
	setsockopt(rawFD, SOL_SOCKET, SO_BINDTODEVICE, interface, sizeof(interface));
	
	//work out the max FD
	int fds[2] = {rawFD, defaultFD};
	int maxfd = 0;
	int i;
	
	for(i=0; i < 2; i++)
	{
		if(fds[i] > maxfd)
		{
			maxfd = fds[i];
		}
	}
	
	while(1)
	{	
		FD_ZERO(&rfdset);
		FD_ZERO(&wfdset);
		FD_SET(rawFD, &wfdset);
		FD_SET(rawFD, &rfdset);
		FD_SET(defaultFD, &rfdset);
		
		struct sockaddr_in sourceAddr;
		
		//IP Header is 24 bytes
		//Leaves 1000 bytes for data
		char packet[1024];
		
		//int selectErr = select(maxfd + 1, &rfdset, &wfdset, NULL, NULL);
		
		if(selectErr == -1)
		{
			//something went wrong.
		}
		
		// First Priority:
		//attempt to clear the release buffer first to the raw socket.
		if(1)
		{
			if(FD_SET(rawFD, &wfdset))
			{
				
			}
		}
		
		// Second Priority:
		//then process packets from the default socket
		if(FD_SET(defaultFD, &rfdset))
		{
			if(recv(defaultFD, (char *)&packet, sizeof(packet), 0))
			{
				//extract the source ip address
				ipheader *iphdr = (ipheader *)&packet;
				
				printf("TTL: = %x\n", iphdr->ip_ttl);
				printf("SRC: = %x\n", iphdr->ip_src);
				printf("DST: = %x\n", iphdr->ip_dst);
				printf("PRO: = %x\n", iphdr->ip_p);
			}
			//extract the destination IP address
			//send a route discovery message to the RE
			//buffer the packet
		}
		
		// Third Priority:
		//then process promiscuous packets from the raw socket.
		if(FD_SET(rawFD, &rfdset))
		{
			//check for protocol matching that of the argument
			//send msg to RE
			//discard packet
		}

	}
}













