// SPDX-License-Identifier: GPL-2.0-or-later
/* Draws each icon the way the shell does (GtkIconPaintable -> snapshot -> GSK cairo renderer) and
 * compares it with the librsvg render of the same SVG at the same size.
 *   gtkcheck <max-rmse> <size> <icon.svg> <librsvg.png> [<icon.svg> <librsvg.png> ...]
 * Prints "<rmse> <size> <icon.svg>" per icon (and FAIL when above the limit); exit 1 when any fails.
 * RMSE: over the premultiplied RGBA channels, each in 0..1 (a pixel weighs by its coverage). Run by check.sh (needs a display:
 * check.sh starts a private broadway one). */
#include <gtk/gtk.h>
#include <math.h>
#include <stdlib.h>

static guchar *rgba(GdkTexture *t, gsize *stride) {
  GdkTextureDownloader *d = gdk_texture_downloader_new(t);
  gdk_texture_downloader_set_format(d, GDK_MEMORY_R8G8B8A8_PREMULTIPLIED);
  GBytes *b = gdk_texture_downloader_download_bytes(d, stride);
  gdk_texture_downloader_free(d);
  gsize n;
  return g_bytes_unref_to_data(b, &n);
}

int main(int argc, char **argv) {
  if (argc < 5 || (argc - 3) % 2) {
    g_printerr("usage: gtkcheck <max-rmse> <size> <icon.svg> <librsvg.png> ...\n");
    return 2;
  }
  gtk_init();
  double max = g_ascii_strtod(argv[1], NULL);
  int size = atoi(argv[2]);
  GskRenderer *r = gsk_cairo_renderer_new();
  GError *e = NULL;
  if (!gsk_renderer_realize_for_display(r, gdk_display_get_default(), &e)) {
    g_printerr("gtkcheck: renderer: %s\n", e->message);
    return 2;
  }
  int bad = 0;
  graphene_rect_t vp = GRAPHENE_RECT_INIT(0, 0, size, size);
  for (int i = 3; i + 1 < argc; i += 2) {
    GFile *f = g_file_new_for_path(argv[i]);
    GtkIconPaintable *p = gtk_icon_paintable_new_for_file(f, size, 1);
    GtkSnapshot *s = gtk_snapshot_new();
    gdk_paintable_snapshot(GDK_PAINTABLE(p), GDK_SNAPSHOT(s), size, size);
    GskRenderNode *node = gtk_snapshot_free_to_node(s);
    GdkTexture *ref = gdk_texture_new_from_filename(argv[i + 1], &e);
    if (!node || !ref) {
      g_printerr("gtkcheck: %s: %s\n", argv[i], node ? e->message : "GTK drew nothing");
      g_clear_error(&e);
      bad++;
      continue;
    }
    GdkTexture *got = gsk_renderer_render_texture(r, node, &vp);
    if (gdk_texture_get_width(ref) != size || gdk_texture_get_height(ref) != size) {
      g_printerr("gtkcheck: %s: reference is not %dx%d\n", argv[i + 1], size, size);
      bad++;
      continue;
    }
    gsize sa, sb;
    guchar *a = rgba(got, &sa), *b = rgba(ref, &sb);
    double sum = 0;
    for (int y = 0; y < size; y++)
      for (int x = 0; x < size * 4; x++) {
        double d = (a[y * sa + x] - b[y * sb + x]) / 255.0;
        sum += d * d;
      }
    double rmse = sqrt(sum / ((double)size * size * 4));
    int fail = !(rmse <= max);
    bad += fail;
    g_print("%.4f %d %s%s\n", rmse, size, argv[i], fail ? "  FAIL" : "");
    g_free(a);
    g_free(b);
    g_object_unref(got);
    g_object_unref(ref);
    gsk_render_node_unref(node);
    g_object_unref(p);
    g_object_unref(f);
  }
  gsk_renderer_unrealize(r);
  return bad ? 1 : 0;
}
