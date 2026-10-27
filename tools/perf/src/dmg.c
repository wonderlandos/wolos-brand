/* Frame-damage clock for latency tests: prints "MONO_MS x y w h" per damage rect of each frame; with "dmg X Y W H", "MONO_MS HASH" of that region per frame (wlr-screencopy
   copy_with_damage, cursor excluded). Run in background, inject input, take the first line after. */
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
#include <time.h>
#include <unistd.h>
#include <wayland-client.h>
#include "sc.h"
static struct wl_shm *shm; static struct wl_output *out; static struct zwlr_screencopy_manager_v1 *mgr;
static struct wl_buffer *buf; static int ready, failed; static int nr; static int R[64][4];
static unsigned char *px; static uint32_t PW,PH,PS; static int gx,gy,gw,gh;
static double now(){ struct timespec t; clock_gettime(CLOCK_MONOTONIC,&t); return t.tv_sec*1e3+t.tv_nsec/1e6; }
static void reg(void *d, struct wl_registry *r, uint32_t n, const char *i, uint32_t v){
 if(!strcmp(i,wl_shm_interface.name)) shm=wl_registry_bind(r,n,&wl_shm_interface,1);
 else if(!strcmp(i,wl_output_interface.name)&&!out) out=wl_registry_bind(r,n,&wl_output_interface,1);
 else if(!strcmp(i,zwlr_screencopy_manager_v1_interface.name)) mgr=wl_registry_bind(r,n,&zwlr_screencopy_manager_v1_interface,3);}
static void regrm(void*d,struct wl_registry*r,uint32_t n){}
static const struct wl_registry_listener rl={reg,regrm};
static void fbuf(void*d,struct zwlr_screencopy_frame_v1*f,uint32_t fmt,uint32_t w,uint32_t h,uint32_t s){
 if(buf) return; int fd=memfd_create("dmg",0); ftruncate(fd,s*h);
 px=mmap(0,s*h,PROT_READ|PROT_WRITE,MAP_SHARED,fd,0); PW=w;PH=h;PS=s;
 struct wl_shm_pool*p=wl_shm_create_pool(shm,fd,s*h); buf=wl_shm_pool_create_buffer(p,0,w,h,s,fmt); wl_shm_pool_destroy(p); close(fd);}
static void fflags(void*d,struct zwlr_screencopy_frame_v1*f,uint32_t fl){}
static void fready(void*d,struct zwlr_screencopy_frame_v1*f,uint32_t a,uint32_t b,uint32_t c){ready=1;}
static void ffail(void*d,struct zwlr_screencopy_frame_v1*f){failed=1;}
static void fdmg(void*d,struct zwlr_screencopy_frame_v1*f,uint32_t x,uint32_t y,uint32_t w,uint32_t h){
 if(nr<64){R[nr][0]=x;R[nr][1]=y;R[nr][2]=w;R[nr][3]=h;nr++;}}
static void fdmabuf(void*d,struct zwlr_screencopy_frame_v1*f,uint32_t a,uint32_t b,uint32_t c){}
static void fbdone(void*d,struct zwlr_screencopy_frame_v1*f){ zwlr_screencopy_frame_v1_copy_with_damage(f,buf); }
static const struct zwlr_screencopy_frame_v1_listener fl={fbuf,fflags,fready,ffail,fdmg,fdmabuf,fbdone};
/* FNV-1a over the region given on the command line (whole output by default). */
static unsigned long sum(void){ unsigned long hsh=1469598103934665603UL;
 for(int y=gy;y<gy+gh&&y<(int)PH;y++) for(int x=gx;x<gx+gw&&x<(int)PW;x++){ unsigned char*q=px+y*PS+x*4;
  for(int k=0;k<3;k++){ hsh^=q[k]; hsh*=1099511628211UL; } } return hsh; }
int main(int c,char**v){
 struct wl_display*dpy=wl_display_connect(0); if(!dpy) return 1;
 struct wl_registry*r=wl_display_get_registry(dpy); wl_registry_add_listener(r,&rl,0); wl_display_roundtrip(dpy);
 if(!mgr) return 1; setvbuf(stdout,0,_IOLBF,0);
 if(c==5){ gx=atoi(v[1]); gy=atoi(v[2]); gw=atoi(v[3]); gh=atoi(v[4]); }
 for(;;){ ready=failed=0; nr=0;
  struct zwlr_screencopy_frame_v1*f=zwlr_screencopy_manager_v1_capture_output(mgr,0,out);
  zwlr_screencopy_frame_v1_add_listener(f,&fl,0);
  while(!ready&&!failed&&wl_display_dispatch(dpy)!=-1);
  if(ready){ double t=now();
   if(c==5) printf("%.1f %lx\n",t,sum());
   else for(int i=0;i<nr;i++) printf("%.1f %d %d %d %d\n",t,R[i][0],R[i][1],R[i][2],R[i][3]); }
  zwlr_screencopy_frame_v1_destroy(f); if(failed) usleep(1000);}
}
