# دليل معامل اليوم الثاني: إدارة الشيفرة والتكامل المستمر

**مخرَج اليوم:** مستودع لتطبيق الكورس على Azure Repos، وتعديل يمر عبر فرع وطلب دمج مربوط بمهمة، وخط تكامل مستمر يشغّل فحص الجودة والاختبارات تلقائيًا مع كل تعديل.

**قبل أن تبدأ** (من نهاية اليوم الأول):

- حساب GitHub تستطيع الدخول إليه.
- منظمة على Azure DevOps باسمك، وفيها مشروع خاص (Private) باسم `report-service`.
- بيئة عمل Codespace مفتوحة على نسختك من مستودع الكورس.

> في كل الأوامر التالية: استبدل `ORG` باسم منظمتك على Azure DevOps.

---

## المعمل 1: المستودع والفرع وطلب الدمج

### 1. انقل الكود إلى Azure Repos

1. في مشروع `report-service` على Azure DevOps افتح **Repos**.
2. اختر **Import a repository** (Import)، والصق رابط نسختك من مستودع الكورس على GitHub، ثم **Import**.
3. بعد انتهاء الاستيراد اضغط **Clone** في أعلى يمين الصفحة، ثم **Generate Git Credentials**. احتفظ بكلمة المرور الظاهرة.
4. في Terminal داخل Codespace:

```bash
cd /workspaces
git config --global credential.helper store
git config --global user.name "اسمك"
git config --global user.email "بريدك"
git clone https://ORG@dev.azure.com/ORG/report-service/_git/report-service
cd report-service
```

عند طلب كلمة المرور الصق الكلمة التي ولّدتها في الخطوة 3.

### 2. أنشئ مهمة في Azure Boards

1. افتح **Boards** ثم **Work items** ثم **New Work Item** ثم **Task**.
2. العنوان: `إضافة حقل رقم المركبة إلى البلاغ`.
3. احفظ، ودوّن رقم المهمة (مثلًا 12).

### 3. أنشئ فرعًا ونفّذ التعديل

```bash
git checkout -b feature/vehicle-plate
```

افتح الملف `app/main.py` وأضف الشرط التالي داخل الدالة `validate_report` قبل السطر `return errors`:

```python
    plate = str(data.get("plate", ""))
    if len(plate) > 10:
        errors.append("plate must be 10 characters or less")
```

وأضف السطر التالي داخل القاموس `report` في الدالة `create_report`:

```python
        "plate": data.get("plate", "").strip(),
```

وغيّر رقم الإصدار في أعلى الملف إلى:

```python
APP_VERSION = "1.1.0"
```

أضف اختبارًا جديدًا في آخر الملف `tests/test_app.py`، واترك قبله سطرين فارغين:

```python
def test_long_plate_is_rejected():
    assert validate_report({"location": "شارع المطار", "type": "other", "plate": "12345678901"})
```

تأكد أن كل الاختبارات تنجح على جهازك قبل الحفظ:

```bash
python -m pytest -q
```

### 4. احفظ التعديل وارفعه

```bash
git add .
git commit -m "Add vehicle plate field #12"
git push -u origin feature/vehicle-plate
```

> استبدل 12 برقم مهمتك. وجود `#رقم` في رسالة الحفظ يربط التعديل بالمهمة.

### 5. افتح طلب دمج (Pull Request)

1. **Repos** ثم **Pull requests** ثم **New pull request**: من `feature/vehicle-plate` إلى `main`.
2. في خانة **Work items to link** اختر مهمتك.
3. أضف زميلك مراجعًا في خانة **Reviewers**.
4. **Create**.

> لإضافة زميلك إلى منظمتك: **Organization settings** ثم **Users** ثم **Add users**، اكتب بريده، واختر مستوى الوصول **Basic** والمشروع `report-service`. أول خمسة مستخدمين بمستوى Basic مجانيون.

### 6. المراجعة والدمج والإصدار

1. زميلك يفتح الطلب، يراجع التغييرات في تبويب **Files**، ويضغط **Approve**.
2. اضغط **Complete** ثم **Complete merge**.
3. في Codespace ضع وسم الإصدار:

```bash
git checkout main
git pull
git tag -a v1.1.0 -m "Add vehicle plate field"
git push origin v1.1.0
```

**تحقق:** في Azure Repos تظهر الوسوم في **Repos** ثم **Tags**، وفي المهمة على Boards يظهر رابط الحفظ وطلب الدمج.

### تمرين إضافي: حل تعارض الدمج (Merge Conflict)

```bash
git checkout -b conflict-a
sed -i 's/APP_VERSION = "1.1.0"/APP_VERSION = "1.2.0"/' app/main.py
git commit -am "Bump to 1.2.0"
git checkout main
sed -i 's/APP_VERSION = "1.1.0"/APP_VERSION = "2.0.0"/' app/main.py
git commit -am "Bump to 2.0.0"
git merge conflict-a
```

سيظهر تعارض. افتح `app/main.py`، اختر القيمة الصحيحة، واحذف علامات `<<<<<<<` و`=======` و`>>>>>>>`، ثم:

```bash
git add app/main.py
git commit -m "Resolve version conflict"
```

---

## المعمل 2: أول خط تكامل مستمر (CI Pipeline)

### 1. أنشئ رمز وصول شخصي (Personal Access Token)

1. من أيقونة الإعدادات أعلى اليمين: **User settings** ثم **Personal access tokens** ثم **New Token**.
2. الاسم: `codespace-agent`، والمدة: 7 أيام.
3. الصلاحيات: **Custom defined** ثم **Show all scopes** ثم **Agent Pools: Read & manage**.
4. **Create**، وانسخ الرمز فورًا لأنه لا يظهر مرة أخرى.

### 2. شغّل الوكيل داخل Codespace

الوكيل (Agent) هو الجهاز الذي ينفّذ خطوات الخط. سنستخدم Codespace نفسه وكيلًا، وهذا مجاني.

افتح Terminal جديدًا (علامة + في لوحة Terminal) ونفّذ:

```bash
cd /workspaces/report-service
bash scripts/setup-agent.sh https://dev.azure.com/ORG الرمز_الذي_نسخته
```

اترك هذا الـ Terminal مفتوحًا. **تحقق:** في **Organization settings** ثم **Agent pools** ثم **Default** ثم **Agents** يظهر وكيلك بحالة **Online**.

### 3. اكتب ملف الخط

في الـ Terminal الأول أنشئ الملف `azure-pipelines.yml` في جذر المستودع بهذا المحتوى:

```yaml
trigger:
  branches:
    include: [main]

pool:
  name: Default

steps:
  - script: python -m pip install -r requirements.txt
    displayName: Install dependencies

  - script: python -m flake8 app tests
    displayName: Lint (code quality)

  - script: python -m pytest --junitxml=test-results.xml
    displayName: Run tests

  - task: PublishTestResults@2
    displayName: Publish test results
    condition: succeededOrFailed()
    inputs:
      testResultsFormat: JUnit
      testResultsFiles: test-results.xml
```

> إن تأخرت: `cp labs/day2/solution/azure-pipelines.yml .`

```bash
git add azure-pipelines.yml
git commit -m "Add CI pipeline"
git push
```

### 4. أنشئ الخط على Azure Pipelines

1. **Pipelines** ثم **New pipeline**.
2. **Azure Repos Git** ثم اختر `report-service`.
3. **Existing Azure Pipelines YAML file**، والمسار `/azure-pipelines.yml`، ثم **Continue** ثم **Run**.
4. إن ظهرت رسالة تطلب صلاحية الوصول إلى مجمع الوكلاء: **View** ثم **Permit**.

**تحقق:** كل الخطوات خضراء، وتبويب **Tests** يعرض 7 اختبارات ناجحة.

### 5. اكسر الخط ثم أصلحه

```bash
sed -i 's/len(location) < 3/len(location) < 1/' app/main.py
git commit -am "Relax location rule"
git push
```

راقب الخط يفشل. افتح خطوة **Run tests**، واقرأ اسم الاختبار الفاشل وسببه. ثم أعد القاعدة كما كانت:

```bash
sed -i 's/len(location) < 1/len(location) < 3/' app/main.py
git commit -am "Restore location rule"
git push
```

### تحدٍّ إضافي: امنع الدمج إذا فشل الخط

1. **Repos** ثم **Branches**، وعند `main` اختر **...** ثم **Branch policies**.
2. فعّل **Require a minimum number of reviewers** (مراجع واحد).
3. في **Build Validation** اضغط **+** واختر خطك.
4. افتح طلب دمج يحتوي اختبارًا فاشلًا، ولاحظ أن زر الدمج لا يعمل حتى ينجح الخط.

---

## مشكلات شائعة

| المشكلة | الحل |
| --- | --- |
| الوكيل يظهر Offline | أُغلق الـ Terminal أو توقفت Codespace. افتحها ونفّذ `cd /workspaces/report-service/agent && ./run.sh` |
| الخط عالق على Queued | تأكد أن الوكيل Online، وأن قسم `pool` في الملف هو `name: Default` |
| `git push` يطلب كلمة مرور مرة بعد مرة | نفّذ `git config --global credential.helper store` ثم أعد المحاولة |
| فشل خطوة Lint | السطر أطول من 120 حرفًا أو فيه مسافات زائدة. اقرأ رقم السطر في السجل وأصلحه |
| `Permission denied` عند تشغيل السكربت | استخدم `bash scripts/setup-agent.sh` لا `./scripts/setup-agent.sh` |

## الخطة البديلة إذا حُجبت المواقع

يعرض المدرب المعملين كاملين من جهازه على الشاشة، وتعمل المجموعات على:

1. قراءة ملف `azure-pipelines.yml` وشرح وظيفة كل سطر.
2. تحديد الخطوة التي ستفشل لو تغيّرت القاعدة في `validate_report`، وسبب فشلها.
3. ترتيب أوامر Git للمعمل الأول على بطاقات ورقية بالترتيب الصحيح.

---

**للمقارنة:** الخط نفسه على GitHub Actions موجود في `labs/day2/solution/github-actions-ci.yml`.
