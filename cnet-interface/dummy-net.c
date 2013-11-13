#include "cnet-interface.h"


//TODO This probably needs tweaking
#define ROUTETIME 5000

QUEUE unrouted;
QUEUE routed;
FILE* in_pipe;
FILE* out_pipe;
off_t in_pos;
off_t out_pos;


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
		//printf("Node %d: Message for %d\n",nodeinfo.address,m->h.dest);
		if(m->h.dest == nodeinfo.address) 
		{	
			//printf("Node %d: receiving message\n");
			size_t len = m->h.len;
			//TODO we're ignoring duplicate messages
			CNET_write_application(m->msg,&len);
		}
		else
		{
			//printf("Node %d: passing message away\n");
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
	printf("%d: Finished net_init()\n",nodeinfo.address);
}

char * join_string(char * str1, char * str2)
{
	char * new_str ;
	if((new_str = malloc(strlen(str1)+strlen(str2)+1)) != NULL){
	    new_str[0] = '\0';   // ensures the memory is an empty string
	    strcat(new_str,str1);
	    strcat(new_str,str2);
	} else {
	    printf("malloc failed!\n");
	}
	return new_str;
}

//read returns 0 if no one has pipe open
//read return -1 if no data + NON_BLOCK (also errno == EAGAIN)
int get_from_pipe(int pipefd, char* buf, size_t bufsiz)
{
	//buf = malloc(bufsiz);
	int num_bytes = 0;
	char * next_char = malloc(1);
	if(read(pipefd,next_char,1) > 0) {
		buf[num_bytes] = *next_char;
		num_bytes++;
		int bytes_read = 1;
		while(bytes_read > 0 && num_bytes < bufsiz-1 && *next_char != '\0') {
			next_char = malloc(1);
			//printf("Read error: %s\n",strerror(errno));
			bytes_read = read(pipefd,next_char,1);
			if(bytes_read > 0) {
				buf[num_bytes] = *next_char;
				num_bytes++;
			}
		}
		//buf[num_bytes] = '\0';
	}
	return num_bytes;
}

EVENT_HANDLER(reboot_node)
{
	//init our pipes
	char * in_pipe_name = "inpipe";
	char * out_pipe_name = "outpipe";
	char node_num[4];
	sprintf(node_num,"%d",nodeinfo.address);
	in_pipe_name = join_string(in_pipe_name,node_num);
	out_pipe_name = join_string(out_pipe_name,node_num);

	unlink(in_pipe_name);
	unlink(out_pipe_name);
	mkfifo(in_pipe_name,S_IRUSR | S_IWUSR);
	mkfifo(out_pipe_name,S_IRUSR | S_IWUSR);
	printf("%d: MADE MY PIPES!\n",nodeinfo.address);
	
	int outFD = open(out_pipe_name, O_NONBLOCK | O_RDWR);
	//TODO if I do NONBLOCK the whole these fdopens return NULL
	//in_pipe = fdopen(inFD,"r");
	out_pipe = fdopen(outFD,"w");
	
	/*
	if(in_pipe != NULL && out_pipe != NULL)
		printf("%d: OPENED MY PIPES!\n",nodeinfo.address);
	else
		exit(0);
	*/

	fprintf(out_pipe,"Hi, I am node %d\n",nodeinfo.address);
	fprintf(out_pipe,"and I like to party\n");
	printf("%d: wrote to pipe!\n",nodeinfo.address);
	
	pid_t child_pid;
	if((child_pid = fork()) < 0 )
	{
		perror("fork failure");
		exit(1);
	}
	if(child_pid == 0)
	{
		execl("/usr/bin/python","/usr/bin/python","cnet_network.py", out_pipe_name, in_pipe_name, (char*)0);
	}
	fclose(out_pipe);
	
	int inFD = open(in_pipe_name, O_NONBLOCK | O_RDWR);
	if(inFD < 0)
		printf("Couldn't open in_pipe\n");
	char buf[100];
	int num_bytes = get_from_pipe(inFD,buf,100);
	while(num_bytes == 0) {
		//printf("Read error: %s\n",strerror(errno));
		num_bytes = get_from_pipe(inFD,buf,100);
	}
	printf("Read %d bytes\n",num_bytes);
	printf("%d: %s\n",nodeinfo.address,buf);
	
	char buf2[100];
	num_bytes = 0;
	while(num_bytes == 0) {
		//printf("Read error: %s\n",strerror(errno));
		num_bytes = get_from_pipe(inFD,buf2,100);
	}
	printf("Read %d bytes\n",num_bytes);
	printf("%d: %s\n",nodeinfo.address,buf2);
	//fclose(in_pipe);

	link_init();
	net_init();
	walking_init();
	CHECK(CNET_enable_application(ALLNODES));
	printf("%d: Reboot complete\n",nodeinfo.address);
}

