# أساسيات هندسة DevOps: مستودع المعامل

مستودع التطبيق العملي لبرنامج **أساسيات هندسة DevOps** (أكاديمية الخوارزمي). التطبيق خدمة ويب صغيرة للإبلاغ عن حادث بسيط، يكبر مع المتدرب يومًا بعد يوم حتى يصبح خط DevOps كاملًا.

## ابدأ هنا

1. اضغط **Fork** لتنشئ نسختك من هذا المستودع.
2. من نسختك: **Code** ثم **Codespaces** ثم **Create codespace on main**.
3. انتظر حتى تكتمل التهيئة، ثم جرّب:

```bash
python -m pytest -q
python -m app.main
```

ستفتح الخدمة على المنفذ 8000.

## محتوى المستودع

| المسار | المحتوى |
| --- | --- |
| `app/` | تطبيق الكورس (Python و Flask) |
| `tests/` | الاختبارات التلقائية |
| `scripts/setup-agent.sh` | تثبيت وكيل Azure Pipelines داخل Codespace |
| `labs/day2/` | دليل معامل اليوم الثاني وحلولها |
| `labs/day3/` | دليل معامل اليوم الثالث وحلولها (Docker والنشر المستمر) |
| `.devcontainer/` | إعدادات بيئة العمل السحابية |

## English

Hands-on lab repository for the *DevOps Engineering Fundamentals* course. Fork it, open a Codespace, and follow `labs/dayN/LAB-DAYN.md`.
