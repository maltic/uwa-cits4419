#include "cnet-interface.h"



#define WALK_FREQUENCY  1000000         // take a step every 1 second
#define MAX_SPEED       10               // metres per WALK_FREQUENCY
#define MIN_PAUSE       1              // in seconds
#define MAX_PAUSE       5              // in seconds
#define MIN_DIST	5		// in meters


CnetPosition mapsize;
CnetTimerID     tid             = NULLTIMER;
bool            paused          = true;

void get_rand_pos(CnetPosition *new, CnetPosition max)
{
	printf("Mapsize: %d %d\n",max.x,max.y);
	new->x = max.x + 10;
	new->y = max.y + 10;
	while(new->x >= max.x || new->y >= max.y) {
		new->x = CNET_rand()%max.x + MIN_DIST;
		new->y = CNET_rand()%max.y + MIN_DIST;
	}
	printf("Destination: %d %d\n",new->x,new->y);
}



EVENT_HANDLER(walker)
{
   static double          dx      = 0.0;
   static double          dy      = 0.0;
   static double          newx    = 0.0;
   static double          newy    = 0.0;
   static int             nsteps  = 0;

    CnetPosition        now;
    CnetTime            movenext;

//  IF PAUSED, WE NEED TO CHOOSE A NEW DESTINATION AND WALKING SPEED
    if(paused) {
        CnetPosition    newdest;

        CHECK(CNET_get_position(&now, NULL));

//  CHOOSE A NEW DESTINATION THAT DOESN'T REQUIRE WALKING THROUGH A WALL!
        do {
            int                 newspeed;
            double              dist;

            newdest     = now;
            get_rand_pos(&newdest,mapsize);

            dx          = newdest.x - now.x;
            dy          = newdest.y - now.y;
            dist        = sqrt(dx*dx + dy*dy);  // only walking in 2D

            newspeed    = CNET_rand() % MAX_SPEED + 1;
            nsteps      = dist / newspeed;
        } while(nsteps < 3);            // ensure we'll take at least 3 steps
//      draw_walk(&now, &newdest);

//  CALCULATE MOVEMENTS PER STEP
        dx      = (dx / nsteps);
        dy      = (dy / nsteps);
        newx    = now.x;
        newy    = now.y;
        paused  = false;                // and off we go....
    }

//  WE'RE WALKING;  DO WE STILL HAVE SOME STEPS TO TAKE?
    if(nsteps > 0) {
        newx    += dx;
        newy    += dy;

        now.x    = newx;
        now.y    = newy;
        now.z    = 0;
        CHECK(CNET_set_position(now));
        paused  = false;
        --nsteps;
        movenext = WALK_FREQUENCY;
    }
//  WE'VE FINISHED WALKING, SO WE PAUSE HERE FOR A WHILE
    else {
        paused  = true;
        nsteps  = 0;
        movenext = (CNET_rand() % (MAX_PAUSE-MIN_PAUSE) + MIN_PAUSE) * 1000000;
    }

//  RESCHEDULE THIS WALKING EVENT
    tid = CNET_start_timer(EV_WALKING, movenext, data);
}


void start_walking()
{
	CNET_stop_timer(tid);
	tid = CNET_start_timer(EV_WALKING, (CNET_rand() % (MAX_PAUSE-MIN_PAUSE) + MIN_PAUSE) * 1000000, 0);
}

void stop_walking()
{
	CNET_stop_timer(tid);
	paused = true;
}

void walking_init()
{
	CNET_srand(nodeinfo.time_of_day.sec + nodeinfo.nodenumber);

	CHECK(CNET_get_position(NULL,&mapsize));


	CnetPosition start;
	get_rand_pos(&start,mapsize);
	CHECK(CNET_set_position(start));
	

	
	CHECK(CNET_set_handler(EV_WALKING, walker, 0));
	start_walking();
}


