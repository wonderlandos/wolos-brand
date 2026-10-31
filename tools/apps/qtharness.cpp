// SPDX-License-Identifier: GPL-2.0-or-later
// Applies a qt6ct config + colour scheme the way qt6ct does (21 roles per group, style, general
// font) and grabs a representative window offscreen. Proof only; WolOS ships the real qt6ct.
// build: g++ -std=c++17 -fPIC qtharness.cpp -o qtharness $(pkg-config --cflags --libs Qt6Widgets)
// usage: QT_QPA_PLATFORM=offscreen qtharness <qt6ct.conf> <out.png>
#include <QApplication>
#include <QCheckBox>
#include <QComboBox>
#include <QGroupBox>
#include <QHBoxLayout>
#include <QLabel>
#include <QLineEdit>
#include <QListWidget>
#include <QProgressBar>
#include <QPushButton>
#include <QRadioButton>
#include <QSettings>
#include <QSlider>
#include <QStyleFactory>
#include <QTabWidget>
#include <QVBoxLayout>

static void load(QPalette &p, QPalette::ColorGroup g, const QStringList &l) {
    for (int i = 0; i < l.size() && i < QPalette::NColorRoles; ++i)
        p.setColor(g, QPalette::ColorRole(i), QColor(l[i].trimmed()));
}

int main(int argc, char **argv) {
    QApplication app(argc, argv);
    QSettings conf(argv[1], QSettings::IniFormat);
    QStyle *st = QStyleFactory::create(conf.value("Appearance/style").toString());
    QApplication::setStyle(st ? st : QStyleFactory::create("Fusion"));  // no Kvantum on the dev host
    QSettings scheme(conf.value("Appearance/color_scheme_path").toString(), QSettings::IniFormat);
    QPalette p;
    load(p, QPalette::Active, scheme.value("ColorScheme/active_colors").toStringList());
    load(p, QPalette::Inactive, scheme.value("ColorScheme/inactive_colors").toStringList());
    load(p, QPalette::Disabled, scheme.value("ColorScheme/disabled_colors").toStringList());
    QApplication::setPalette(p);
    QFont f;
    f.fromString(conf.value("Fonts/general").toString());
    QApplication::setFont(f);

    QWidget w;
    auto *v = new QVBoxLayout(&w);
    auto *tabs = new QTabWidget;
    auto *page = new QWidget;
    auto *pv = new QVBoxLayout(page);
    auto *row = new QHBoxLayout;
    row->addWidget(new QLineEdit("Search documents"));
    auto *combo = new QComboBox;
    combo->addItems({"All files", "Images"});
    row->addWidget(combo);
    auto *def = new QPushButton("Open");
    def->setDefault(true);
    row->addWidget(def);
    row->addWidget(new QPushButton("Cancel"));
    pv->addLayout(row);
    auto *list = new QListWidget;
    list->addItems({"Budget 2026.ods", "Holiday photos", "Notes.txt", "Report.odt"});
    list->setCurrentRow(1);
    pv->addWidget(list);
    auto *opts = new QGroupBox("Options");
    auto *ov = new QHBoxLayout(opts);
    auto *c = new QCheckBox("Show hidden files");
    c->setChecked(true);
    ov->addWidget(c);
    auto *r = new QRadioButton("Icons");
    r->setChecked(true);
    ov->addWidget(r);
    ov->addWidget(new QRadioButton("List"));
    auto *dis = new QPushButton("Disabled");
    dis->setEnabled(false);
    ov->addWidget(dis);
    pv->addWidget(opts);
    auto *s = new QSlider(Qt::Horizontal);
    s->setValue(60);
    pv->addWidget(s);
    auto *pb = new QProgressBar;
    pb->setValue(40);
    pv->addWidget(pb);
    tabs->addTab(page, "Files");
    tabs->addTab(new QLabel("Second"), "Settings");
    v->addWidget(tabs);
    w.resize(560, 420);
    w.show();
    app.processEvents();
    w.grab().save(argv[2]);
    return 0;
}
