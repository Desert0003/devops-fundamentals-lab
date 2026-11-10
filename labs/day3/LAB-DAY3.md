# دليل معامل اليوم الثالث: النشر المستمر والحاويات

> الخطوات المختصرة. الحلول الكاملة في `labs/day3/solution/`.

> نبني على ما انتهى إليه اليوم الثاني: مستودع `report-service` على Azure Repos، وخط تكامل يعمل على الوكيل داخل Codespace، والفرع `main` محمي.

> في كل الأوامر: استبدل `ORG` باسم منظمتك على Azure DevOps.

| المعمل | المحتوى | الزمن التقريبي |
| --- | --- | --- |
| الأول | التطبيق في حاوية Docker | 45 دقيقة |
| الثاني | خط نشر: dev ثم test ثم prod بموافقة | 45 دقيقة |
| الثالث | إصدار معيب، ثم تراجع، ثم إصلاح | 50 دقيقة |
| إضافي | رفع الصورة إلى GitHub Container Registry | 15 دقيقة |

---

## قبل أن تبدأ

1. على GitHub افتح نسختك من `devops-fundamentals-lab`، ثم **Sync fork** ثم **Update branch**.
2. في Codespace، تأكد أن الوكيل يعمل. إن توقف:

```bash
cd ~/azagent && ./run.sh
```

3. في Terminal آخر، اسحب ملفات اليوم الثالث إلى نسخة GitHub:

```bash
cd /workspaces/devops-fundamentals-lab
git pull
ls labs/day3/solution
```

> ✓ تظهر الملفات: `Dockerfile` و`azure-pipelines.yml` و`rollback.yml` ومجلد `templates`

> ⚠️ أوامر المعامل كلها في `/workspaces/report-service`، إلا أوامر النسخ من مجلد الحلول.

---

## المعمل الأول: التطبيق في حاوية

### 1. فرع جديد

```bash
cd /workspaces/report-service
git checkout main
git pull
git checkout -b feature/containerize
```

### 2. التطبيق يعرف بيئته

الصورة نفسها ستعمل في ثلاث بيئات، وكل بيئة تخبرها باسمها عبر متغير بيئة.

```bash
code app/main.py
```

1. أضف في أول سطر استيراد:

```python
import os
```

2. تحت سطر `INCIDENT_TYPES` أضف:

```python
APP_ENV = os.environ.get("APP_ENV", "local")
```

3. غيّر رقم الإصدار:

```python
APP_VERSION = "1.2.0"
```

4. في الدالة `index` أضف `env=APP_ENV` إلى `render_template`:

```python
    return render_template("index.html", version=APP_VERSION, env=APP_ENV, reports=list(reversed(_reports)))
```

5. في الدالة `health`:

```python
    return jsonify(status="ok", version=APP_VERSION, env=APP_ENV)
```

6. اعرض البيئة في رأس الصفحة:

```bash
code app/templates/index.html
```

```html
    <small>الإصدار {{ version }} · البيئة {{ env }}</small>
```

7. أضف اختبارًا في آخر `tests/test_app.py` بعد سطرين فارغين:

```python
def test_health_reports_environment(client):
    assert client.get("/health").get_json()["env"] == "local"
```

8. افحص:

```bash
python -m pytest -q
python -m flake8 app tests
```

> ✓ 8 passed، ولا يطبع flake8 شيئًا

### 3. ملف الحاوية

انسخ الملفين، ثم افتح `Dockerfile` واقرأه سطرًا سطرًا:

```bash
cp /workspaces/devops-fundamentals-lab/labs/day3/solution/Dockerfile .
cp /workspaces/devops-fundamentals-lab/labs/day3/solution/.dockerignore .
code Dockerfile
```

### 4. ابنِ الصورة وشغّلها

```bash
docker build -t report-service:1.2.0 .
docker images report-service
docker run -d --name rs-local -p 8080:8000 report-service:1.2.0
docker ps
```

> ✓ بعد نحو 10 ثوانٍ تظهر الحالة `(healthy)`

```bash
curl localhost:8080/health
docker logs rs-local
docker exec rs-local whoami
```

> ✓ `"env":"local"` و`"version":"1.2.0"`، والمستخدم `appuser` لا `root`

افتح المنفذ 8080 من تبويب **Ports** وأرسل بلاغًا من الصفحة.

### 5. الصورة نفسها، بيئة أخرى

```bash
docker run -d --name rs-demo -p 8090:8000 -e APP_ENV=demo report-service:1.2.0
curl localhost:8090/health
docker rm -f rs-local rs-demo
```

> ✓ `"env":"demo"`: الصورة لم تتغير، تغيّر الإعداد فقط

### 6. احفظ وادمج

```bash
git add .
git commit -m "Containerize the service and expose its environment"
git push -u origin HEAD
```

افتح طلب دمج إلى `main`، وانتظر نجاح الخط، ثم **Approve** و**Complete** بـ **Squash commit**.

---

## المعمل الثاني: خط نشر إلى ثلاث بيئات

### 1. ملفات الخط

```bash
cd /workspaces/report-service
git checkout main
git pull
git checkout -b feature/cd-pipeline
mkdir -p templates
cp /workspaces/devops-fundamentals-lab/labs/day3/solution/azure-pipelines.yml .
cp /workspaces/devops-fundamentals-lab/labs/day3/solution/rollback.yml .
cp /workspaces/devops-fundamentals-lab/labs/day3/solution/templates/deploy.yml templates/
code azure-pipelines.yml
```

اقرأ الملف: مرحلة **Build** تبني الصورة مرة واحدة، ثم **Dev** و**Test** و**Prod** تنشر الصورة نفسها، كل بيئة على منفذ.

| البيئة | المنفذ |
| --- | --- |
| dev | 8081 |
| test | 8082 |
| prod | 8083 |

### 2. طلب الدمج

```bash
git add .
git commit -m "Add multi-stage CD pipeline and rollback pipeline"
git push -u origin HEAD
```

1. افتح طلب دمج إلى `main`.

> ✓ خط الطلب يشغّل **Build** فقط، وتظهر مراحل النشر **Skipped**: لا ننشر كودًا لم يُدمج بعد

2. **Approve** ثم **Complete** بـ **Squash commit**.

### 3. أول نشر

1. **Pipelines**، ثم التشغيل الجديد على `main`.
2. إن ظهر **This pipeline needs permission to access a resource**: **View** ثم **Permit** لكل بيئة.

> ✓ أربع مراحل خضراء: Build ثم Dev ثم Test ثم Prod

3. من تبويب **Ports** افتح 8081 ثم 8082 ثم 8083.

> ✓ الإصدار 1.2.0 في الثلاث، والبيئة تختلف: dev ثم test ثم prod

4. **Pipelines** ثم **Environments**: لكل بيئة سجل بما نُشر فيها ومتى.

### 4. بوابة الموافقة قبل الإنتاج

1. **Pipelines** ثم **Environments** ثم **prod**.
2. **⋯** أعلى اليمين ثم **Approvals and checks** ثم **+** ثم **Approvals**.
3. أضف نفسك في **Approvers**، ثم **Create**.

> ✓ من الآن لا يصل أي إصدار إلى prod قبل موافقتك

---

## المعمل الثالث: إصدار معيب، ثم تراجع

### 1. زميل مستعجل

```bash
cd /workspaces/report-service
git checkout main
git pull
git checkout -b feature/new-title
code app/templates/index.html
```

1. غيّر العنوان إلى:

```html
    <h2>خدمة الإبلاغ عن الحوادث البسيطة</h2>
```

2. وفي سطر `small` احذف قوسًا واحدًا من `{{ env }}` ليصبح `{{ env }`، كأنه خطأ سهو.

3. في `app/main.py` غيّر الإصدار إلى `1.3.0`، ثم:

```bash
python -m pytest -q
python -m flake8 app tests
```

> ✓ 8 passed: الاختبارات لا تفحص الصفحة الرئيسية

```bash
git commit -am "Update page title"
git push -u origin HEAD
```

افتح طلب دمج، ثم **Approve** و**Complete**.

### 2. الإصدار يمر

1. في **Pipelines** يعمل الخط: Build ثم Dev ثم Test، كلها خضراء.
2. مرحلة **Prod** تنتظر: **Review** ثم **Approve**.
3. افتح المنفذ 8083.

> ✓ خطأ `Internal Server Error`: الإنتاج معطّل، مع أن الخط كله أخضر

> ⚠️ نقاش: لماذا نجح فحص الدخان؟ وماذا كان يجب أن يفحص المعتمد قبل الموافقة؟

### 3. التراجع

1. **Pipelines** ثم **New pipeline** ثم **Azure Repos Git** ثم **report-service**.
2. **Existing Azure Pipelines YAML file**، والمسار `/rollback.yml`، ثم **Continue**.
3. بجانب زر **Run** اضغط السهم ▾ ثم **Save**.
4. **Run pipeline**، وفي **Version** اكتب `1.2.0`، ثم **Run**.
5. **Permit** إن طُلب، ثم وافق على النشر إلى prod.

> ✓ المنفذ 8083 يعمل من جديد بالإصدار 1.2.0، خلال دقيقة وبلا أي تعديل في الكود

### 4. الإصلاح وسد الثغرة

```bash
git checkout main
git pull
git checkout -b fix/home-page
```

1. أعد القوس: `{{ env }}`، وغيّر الإصدار إلى `1.3.1`.
2. أضف فحصًا للصفحة الرئيسية في آخر `templates/deploy.yml`:

```yaml

  - script: curl -fsS -o /dev/null http://localhost:${{ parameters.port }}/
    displayName: Smoke test home page ${{ parameters.envName }}
```

```bash
python -m pytest -q
git add .
git commit -m "Fix home page and smoke-test it on every deploy"
git push -u origin HEAD
```

افتح طلب دمج، وأكمله، ثم وافق على prod.

> ✓ الإصدار 1.3.1 في البيئات الثلاث، وكل نشر صار يفحص الصفحة الرئيسية

---

## إضافي: رفع الصورة إلى GitHub Container Registry

1. على GitHub: صورتك ثم **Settings** ثم **Developer settings** ثم **Personal access tokens** ثم **Tokens (classic)** ثم **Generate new token (classic)**.
2. الاسم `ghcr-push`، والمدة 7 أيام، والصلاحية `write:packages` فقط، ثم **Generate token** وانسخه.
3. في Azure: **Pipelines** ثم خطك ثم **Edit** ثم **Variables** ثم **New variable**:
   - `GHCR_USER`: اسم حسابك على GitHub
   - `GHCR_TOKEN`: الرمز، مع تفعيل **Keep this value secret**
4. **Save**، ثم **Run pipeline**، ووافق على prod.

> ✓ مرحلة **Publish** خضراء، والصورة `report-service:1.3.1` تظهر في حسابك على GitHub تحت **Packages**

> ⚠️ الرمز لا يُكتب في أي ملف، ولا يظهر في أي لقطة شاشة. المتغير السري لا يُطبع في السجل.

---

## مشكلات شائعة

| العَرَض | السبب | الحل |
| --- | --- | --- |
| `permission denied` عند أوامر `docker` | الـ Terminal قديم | افتح Terminal جديدًا |
| الخط عالق على Queued | الوكيل متوقف | `cd ~/azagent && ./run.sh` |
| مرحلة تنتظر دون سبب ظاهر | تنتظر إذنًا أو موافقة | افتح التشغيل: **Permit** أو **Review** |
| المنفذ لا يفتح | لم يُحوَّل بعد | تبويب **Ports** ثم **Forward a Port** |
| `Image report-service:X not found` في التراجع | الإصدار لم يُبنَ على هذا الوكيل | `docker images report-service` واختر إصدارًا موجودًا |
