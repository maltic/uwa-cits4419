#include "cnet-interface.h"


//TODO This probably needs tweaking
#define ROUTETIME 1000000

QUEUE new_messages;
QUEUE unrouted;
QUEUE routed;
FILE* in_pipe;
FILE* out_pipe;
int inFD;
int outFD;


typedef struct
{
	MSGHEADER h;
	char msg[MAX_MESSAGE_SIZE];

} MSG;


char** str_split(char* a_str, const char a_delim)
{
    char** result    = 0;
    size_t count     = 0;
    char* tmp        = a_str;
    char* last_comma = 0;

    /* Count how many elements will be extracted. */
    while (*tmp)
    {
        if (a_delim == *tmp)
        {
            count++;
            last_comma = tmp;
        }
        tmp++;
    }

    /* Add space for trailing token. */
    count += last_comma < (a_str + strlen(a_str) - 1);

    /* Add space for terminating null string so caller
       knows where the list of returned strings ends. */
    count++;

    result = malloc(sizeof(char*) * count);

    if (result)
    {
        size_t idx  = 0;
        char* token = strtok(a_str, ",");

        while (token)
        {
            assert(idx < count);
            *(result + idx++) = strdup(token);
            token = strtok(0, ",");
        }
        assert(idx == count - 1);
        *(result + idx) = 0;
    }

    return result;
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
		memcpy((buf+num_bytes),next_char,1);
		num_bytes++;
		int bytes_read = 1;
		while(bytes_read > 0 && num_bytes < bufsiz-1 && *next_char != '\n') {
			//printf("Read error: %s\n",strerror(errno));
			bytes_read = read(pipefd,next_char,1);
			if(bytes_read > 0) {
				memcpy((buf+num_bytes),next_char,1);
				num_bytes++;
			}
		}
		buf[num_bytes-1] = '\0';
		printf("%d: Got something from pipe %s\n",nodeinfo.address,buf);
	}
	free(next_char);
	return num_bytes;
}


EVENT_HANDLER(app_rdy)
{
	//printf("%d: Making a message\n",nodeinfo.address);
	char* msg = malloc((MAX_MESSAGE_SIZE));
        int dest;
        size_t len = MAX_MESSAGE_SIZE;
        CHECK(CNET_read_application(&dest, msg, &len));
        //printf("%d: got message from CNET\n",nodeinfo.address);
        char* final_msg = malloc((MAX_MESSAGE_SIZE+1));
        memcpy(final_msg,msg,len);
        //printf("%d: copied message\n",nodeinfo.address);
        *(final_msg+(len)) = '\0';
        //printf("%d: reallocated\n",nodeinfo.address);
	printf("%d: Made %d bytes for %d\n",nodeinfo.address,len,dest);
	
	char buf[500];
	int final_len = sprintf(buf,"MSG.%s.%d\n",final_msg,dest);
	write(outFD,buf,final_len);
	
	/*
	int num_bytes = 0;
	if((num_bytes = fprintf(out_pipe,"MSG.%s.%d\n",final_msg,dest)) < 0) {
		printf("%s\n",strerror(errno));
	}
	printf("%d: wrote %d bytes to my dsr\n",nodeinfo.address,num_bytes);
	*/
}

EVENT_HANDLER(get_routed_messages)
{
	//printf("%d: Starting routing\n",nodeinfo.address);
	//what SHOULD happen
	//check unrouted queue, send everything to dsr for routing
	//after this check DSR in_box for messages for app layer
	//then check DSR out_box for things that need forwarding

	//send messages that need routing to routing layer
	//QUEUE to_route = queue_new();
	while(queue_nitems(unrouted) > 0) {
		size_t len;
		char* m = queue_remove(unrouted,&len);
		char* mtemp = malloc(sizeof(char)*(len+1));
		memcpy(mtemp,m,len);
		mtemp[len] = '\0';
		char buf[500];
		int final_len = sprintf(buf,"PKT.%s\n",mtemp);
		write(outFD,buf,final_len);
		//fprintf(out_pipe,"PKT.%s\n",m->msg);
		free(m);
		free(mtemp);
	}
	//push everything down everything in to_route to routing layer
	//for now we just don't route them, we just flood one hop

	//check pipe for messages for app layer or forwarding
	char buf[500];
	while(get_from_pipe(inFD,buf,500) > 0) {
		printf("%d: Reading message from dsr: %s\n",nodeinfo.address,buf);
		char type[10];
		char contents[100];
		char* tok = strtok(buf,".");
		if(tok != NULL) {
			strcpy(type,tok);
			tok = strtok(NULL,".");
			if(tok == NULL) {
				printf("%d: SHIIIIIIITTTTT\n",nodeinfo.address);
				break;
			}
			strcpy(contents,tok);
			if(strcmp(type,"MSG") == 0) {
				printf("%d: A MESSAGE FOR ME!\n",nodeinfo.address);
				size_t len = strlen(contents);
				//len = len-1;
				CNET_write_application(contents,&len);
			} else if(strcmp(type,"FWD") == 0) {
				//printf("%d: getting fwd %s\n",nodeinfo.address,contents);
				queue_add(routed,contents,strlen(contents));
			}
		}
	}
	//then push everything down to the link layer
	while(queue_nitems(routed) > 0) {
		//printf("%d: forwarding messages\n",nodeinfo.address);
		char *next;
		size_t len;
		next = queue_remove(routed,&len);
		link_send_data(next,len);
		free(next);
	}
	CNET_start_timer(EV_DO_ROUTING, ROUTETIME, 1);
}

void net_recv(void* msg, int len)
{
	//enqueue for routing
	//printf("%d: received from physical: %s\n",nodeinfo.address,msg
	queue_add(unrouted,msg,len);
}

void net_init()
{
	unrouted = queue_new();
	routed = queue_new();
	new_messages = queue_new();
	CNET_set_handler(EV_APPLICATIONREADY, app_rdy, 0);
	CNET_set_handler(EV_DO_ROUTING,get_routed_messages,0);
	CNET_start_timer(EV_DO_ROUTING, ROUTETIME, 1);
	printf("%d: Finished net_init()\n",nodeinfo.address);
}



EVENT_HANDLER(shutdown)
{
	printf("%d: SHUTTING DOWN\n",nodeinfo.address);
	fprintf(out_pipe,"shutdown\n");
	fflush(stdout);
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
	mkfifo(in_pipe_name, 0777);
	mkfifo(out_pipe_name, 0777);
	printf("%d: MADE MY PIPES!\n",nodeinfo.address);
	
	outFD = open(out_pipe_name, O_NONBLOCK | O_RDWR);
	//TODO if I do NONBLOCK the whole these fdopens return NULL
	//in_pipe = fdopen(inFD,"r");
	out_pipe = fdopen(outFD,"w+");
	
	/*
	if(in_pipe != NULL && out_pipe != NULL)
		printf("%d: OPENED MY PIPES!\n",nodeinfo.address);
	else
		exit(0);
	*/

	char* message = "Hi, I am a node\n";
	write(outFD,message,strlen(message));
	//fprintf(out_pipe,"Hi, I am node %d\n",nodeinfo.address);
	//fprintf(out_pipe,"and I like to party\n");
	printf("%d: wrote to pipe!\n",nodeinfo.address);
	
	pid_t child_pid;
	if((child_pid = fork()) < 0 )
	{
		perror("fork failure");
		exit(1);
	}
	if(child_pid == 0)
	{
		printf("%d: Starting python dsr \n",nodeinfo.address);
		execl("/home/uniwa/students/students7/20515347/linux/python3/bin/python3","/home/uniwa/students/students7/20515347/linux/python3/bin/python3","cnet_network.py", out_pipe_name, in_pipe_name, (char*)0);
	}
	//fclose(out_pipe);
	
	inFD = open(in_pipe_name, O_NONBLOCK | O_RDWR);
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
	CHECK(CNET_set_handler(EV_SHUTDOWN, shutdown, 0));
	CHECK(CNET_enable_application(ALLNODES));
	printf("%d: Reboot complete\n",nodeinfo.address);
}

