/* SPDX-License-Identifier: GPL-2.0-or-later */
/* Live-test pointer injector: vp move X Y | vp click X Y [n] | vp drag X1 Y1 X2 Y2  (output 1280x800). */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <time.h>
#include <wayland-client.h>
#include "vp.h"
#define BTN_LEFT 0x110
static struct wl_seat*seat; static struct zwlr_virtual_pointer_manager_v1*mgr; static struct zwlr_virtual_pointer_v1*p; static struct wl_display*d;
static void reg(void*x,struct wl_registry*r,uint32_t n,const char*i,uint32_t v){
 if(!strcmp(i,wl_seat_interface.name)&&!seat) seat=wl_registry_bind(r,n,&wl_seat_interface,1);
 else if(!strcmp(i,zwlr_virtual_pointer_manager_v1_interface.name)) mgr=wl_registry_bind(r,n,&zwlr_virtual_pointer_manager_v1_interface,1);}
static void rm(void*x,struct wl_registry*r,uint32_t n){}
static const struct wl_registry_listener rl={reg,rm};
static uint32_t ms(void){struct timespec t;clock_gettime(CLOCK_MONOTONIC,&t);return t.tv_sec*1000+t.tv_nsec/1000000;}
static void mv(int x,int y){zwlr_virtual_pointer_v1_motion_absolute(p,ms(),x,y,1280,800);zwlr_virtual_pointer_v1_frame(p);wl_display_roundtrip(d);usleep(30000);}
static double mono(void){struct timespec t;clock_gettime(CLOCK_MONOTONIC,&t);return t.tv_sec*1e3+t.tv_nsec/1e6;}
/* STAMP=1: print the monotonic ms each release (GTK click) is sent. */
static void btn(int down){if(!down&&getenv("STAMP"))fprintf(stderr,"%.1f\n",mono());zwlr_virtual_pointer_v1_button(p,ms(),BTN_LEFT,down);zwlr_virtual_pointer_v1_frame(p);wl_display_roundtrip(d);usleep(40000);}
int main(int c,char**v){ if(c<4) return 64;
 d=wl_display_connect(0); struct wl_registry*r=wl_display_get_registry(d); wl_registry_add_listener(r,&rl,0); wl_display_roundtrip(d);
 if(!mgr) {fprintf(stderr,"no virtual pointer\n");return 1;}
 p=zwlr_virtual_pointer_manager_v1_create_virtual_pointer(mgr,seat);
 int x=atoi(v[2]),y=atoi(v[3]); mv(x,y);
 if(!strcmp(v[1],"click")){int n=c>4?atoi(v[4]):1; for(int i=0;i<n;i++){btn(1);btn(0);}}
 else if(!strcmp(v[1],"drag")&&c>5){btn(1); int x2=atoi(v[4]),y2=atoi(v[5]); for(int i=1;i<=10;i++) mv(x+(x2-x)*i/10,y+(y2-y)*i/10); btn(0);}
 return 0;}
