// SPDX-License-Identifier: GPL-2.0-or-later
/* Draws each icon the way a Qt app on WolOS does (QSvgRenderer, the QtSvg module the Qt icon
 * engine loads SVG theme icons with) and compares it with the librsvg render of the same SVG.
 *   qtcheck <max-rmse> <size> <icon.svg> <librsvg.png> [<icon.svg> <librsvg.png> ...]
 * QTCHECK_OUT=<dir> also writes each Qt render there as <dir>/<parent>-<name>-<size>.png (for review).
 * Prints "<rmse> <size> <icon.svg>" per icon (and FAIL when above the limit); exit 1 when any fails.
 * RMSE: over the premultiplied RGBA channels, each in 0..1, the same measure as gtkcheck.c.
 * QtSvg draws SVG Tiny with extensions and silently leaves out what it does not support (6.12:
 * clip-path; filters before 6.7), which is what this catches. Run by check.sh. */
#include <QtGui/QGuiApplication>
#include <QtGui/QImage>
#include <QtCore/QDir>
#include <QtCore/QFileInfo>
#include <QtGui/QPainter>
#include <QtSvg/QSvgRenderer>
#include <cmath>
#include <cstdio>
#include <cstdlib>

int main(int argc, char **argv) {
  if (argc < 5 || (argc - 3) % 2) {
    std::fprintf(stderr, "usage: qtcheck <max-rmse> <size> <icon.svg> <librsvg.png> ...\n");
    return 2;
  }
  QGuiApplication app(argc, argv);
  const double max = std::atof(argv[1]);
  const int size = std::atoi(argv[2]);
  int bad = 0;
  for (int i = 3; i + 1 < argc; i += 2) {
    QSvgRenderer svg{QString::fromLocal8Bit(argv[i])};
    QImage ref(QString::fromLocal8Bit(argv[i + 1]));
    if (!svg.isValid() || ref.isNull()) {
      std::fprintf(stderr, "qtcheck: %s: %s\n", argv[i], svg.isValid() ? "no reference PNG" : "QtSvg cannot read it");
      bad++;
      continue;
    }
    if (ref.width() != size || ref.height() != size) {
      std::fprintf(stderr, "qtcheck: %s: reference is not %dx%d\n", argv[i + 1], size, size);
      bad++;
      continue;
    }
    QImage got(size, size, QImage::Format_RGBA8888_Premultiplied);
    got.fill(Qt::transparent);
    {
      QPainter p(&got);
      p.setRenderHint(QPainter::Antialiasing);
      p.setRenderHint(QPainter::SmoothPixmapTransform);
      svg.render(&p, QRectF(0, 0, size, size));
    }
    const QByteArray out = qgetenv("QTCHECK_OUT");
    if (!out.isEmpty()) {
      const QFileInfo fi(QString::fromLocal8Bit(argv[i]));
      got.save(QDir(QString::fromLocal8Bit(out)).filePath(
          QStringLiteral("%1-%2-%3.png").arg(fi.dir().dirName(), fi.completeBaseName()).arg(size)));
    }
    ref = ref.convertToFormat(QImage::Format_RGBA8888_Premultiplied);
    double sum = 0;
    for (int y = 0; y < size; y++) {
      const uchar *a = got.constScanLine(y), *b = ref.constScanLine(y);
      for (int x = 0; x < size * 4; x++) {
        const double d = (a[x] - b[x]) / 255.0;
        sum += d * d;
      }
    }
    const double rmse = std::sqrt(sum / (double(size) * size * 4));
    const bool fail = !(rmse <= max);
    bad += fail;
    std::printf("%.4f %d %s%s\n", rmse, size, argv[i], fail ? "  FAIL" : "");
  }
  return bad ? 1 : 0;
}
