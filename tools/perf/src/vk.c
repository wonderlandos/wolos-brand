/* Live-test key injector: vk TEXT | vk -k KEYSYM_NAME [-m super|shift|...] ; zwp_virtual_keyboard_v1. */
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
#include <unistd.h>
#include <time.h>
#include <wayland-client.h>
#include <xkbcommon/xkbcommon.h>
#include "vk.h"
static struct wl_seat *seat; static struct zwp_virtual_keyboard_manager_v1 *mgr;
static void reg(void*d,struct wl_registry*r,uint32_t n,const char*i,uint32_t v){
 if(!strcmp(i,wl_seat_interface.name)&&!seat) seat=wl_registry_bind(r,n,&wl_seat_interface,1);
 else if(!strcmp(i,zwp_virtual_keyboard_manager_v1_interface.name)) mgr=wl_registry_bind(r,n,&zwp_virtual_keyboard_manager_v1_interface,1);}
static void rm(void*d,struct wl_registry*r,uint32_t n){}
static const struct wl_registry_listener rl={reg,rm};
static struct xkb_keymap*km; static struct zwp_virtual_keyboard_v1*kb; static struct wl_display*dpy;
static uint32_t ms(void){struct timespec t;clock_gettime(CLOCK_MONOTONIC,&t);return t.tv_sec*1000+t.tv_nsec/1000000;}
static int code_for(xkb_keysym_t ks,int*shift){
 for(xkb_keycode_t k=xkb_keymap_min_keycode(km);k<=xkb_keymap_max_keycode(km);k++)
  for(int lvl=0;lvl<2;lvl++){const xkb_keysym_t*s;int n=xkb_keymap_key_get_syms_by_level(km,k,0,lvl,&s);
   for(int i=0;i<n;i++) if(s[i]==ks){*shift=lvl;return k-8;}}
 return -1;}
static double mono(void){struct timespec t;clock_gettime(CLOCK_MONOTONIC,&t);return t.tv_sec*1e3+t.tv_nsec/1e6;}
/* STAMP=1: print the monotonic ms each key press is sent (latency tests). */
static void key(int code,int down){if(down&&getenv("STAMP"))fprintf(stderr,"%.1f\n",mono());zwp_virtual_keyboard_v1_key(kb,ms(),code,down);wl_display_roundtrip(dpy);usleep(20000);}
static void mods(uint32_t m){zwp_virtual_keyboard_v1_modifiers(kb,m,0,0,0);wl_display_roundtrip(dpy);}
int main(int c,char**v){
 dpy=wl_display_connect(0); if(!dpy) return 1;
 struct wl_registry*r=wl_display_get_registry(dpy); wl_registry_add_listener(r,&rl,0); wl_display_roundtrip(dpy);
 if(!mgr||!seat){fprintf(stderr,"no virtual keyboard\n");return 1;}
 struct xkb_context*ctx=xkb_context_new(0); struct xkb_rule_names names={0}; names.layout="us";
 km=xkb_keymap_new_from_names(ctx,&names,0); char*str=xkb_keymap_get_as_string(km,XKB_KEYMAP_FORMAT_TEXT_V1);
 size_t len=strlen(str)+1; int fd=memfd_create("km",0); write(fd,str,len);
 kb=zwp_virtual_keyboard_manager_v1_create_virtual_keyboard(mgr,seat);
 zwp_virtual_keyboard_v1_keymap(kb,WL_KEYBOARD_KEYMAP_FORMAT_XKB_V1,fd,len); wl_display_roundtrip(dpy);
 uint32_t altm=1<<xkb_keymap_mod_get_index(km,XKB_MOD_NAME_ALT), shiftm=1<<xkb_keymap_mod_get_index(km,XKB_MOD_NAME_SHIFT), superm=1<<xkb_keymap_mod_get_index(km,XKB_VMOD_NAME_SUPER);
 if(xkb_keymap_mod_get_index(km,XKB_VMOD_NAME_SUPER)==XKB_MOD_INVALID) superm=1<<xkb_keymap_mod_get_index(km,XKB_MOD_NAME_LOGO);
 if(c>=3&&!strcmp(v[1],"-k")){ /* vk -k Keysym [super] [shift] */
  uint32_t m=0; int sh; for(int i=3;i<c;i++){ if(!strcmp(v[i],"super")) m|=superm; if(!strcmp(v[i],"shift")) m|=shiftm; if(!strcmp(v[i],"alt")) m|=altm; }
  int code=code_for(xkb_keysym_from_name(v[2],0),&sh); if(code<0) return 2;
  if(m) mods(m); key(code,1); key(code,0); if(m) mods(0); return 0; }
 if(c>=3&&(!strcmp(v[1],"-d")||!strcmp(v[1],"-u"))){ int sh; int code=code_for(xkb_keysym_from_name(v[2],0),&sh); key(code,!strcmp(v[1],"-d")); return 0;}
 for(char*p=v[1];p&&*p;p++){ int sh; int code=code_for(xkb_utf32_to_keysym((unsigned char)*p),&sh); if(code<0) continue;
  if(sh) mods(shiftm); key(code,1); key(code,0); if(sh) mods(0);}
 return 0;}
