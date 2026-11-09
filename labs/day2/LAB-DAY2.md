# دليل معامل اليوم الثاني: إدارة الشيفرة والتكامل المستمر

> الخطوات المختصرة. الشرح الكامل لكل خطوة في دليل المعامل (Lab Guide) الذي يوزعه المدرب.

> في كل الأوامر: استبدل `ORG` باسم منظمتك على Azure DevOps، و`ID` برقم مهمتك.

---

## المعمل الأول: من المهمة إلى الإصدار

### 1. نسخة المشروع (تمت في اليوم الأول)

> ⚠️ إن كانت بيئتك تعمل وظهر لك 6 passed أمس، فابدأ من الخطوة 5.

1. github.com/settings/codespaces ثم Default idle timeout، واكتب 240، ثم Save. ينطبق على البيئات الجديدة فقط.

2. افتح github.com/ziad201189/devops-fundamentals-lab ثم Fork ثم Create fork.

3. من نسختك: Code ثم Codespaces ثم Create codespace on main.

4. في الـ Terminal:

```bash
python -m pytest -q
```

> ✓ 6 passed

### 2. Azure DevOps

5. افتح dev.azure.com، وأنشئ مشروعًا report-service بخصوصية Private. إن أنشأته أمس فتخطَّ هذه الخطوة.

6. Boards ثم Work items ثم New Work Item ثم Task، والعنوان Add vehicle plate field to incident report، ثم Save، ودوّن رقم المهمة (ID).

### 3. المستودع

7. Repos ثم Import a repository، والصق رابط نسختك على GitHub، ثم Import.

8. Clone ثم Generate Git Credentials، وانسخ كلمة المرور.

9. كل سطر وحده، واستبدل ORG باسم منظمتك:

```bash
cd /workspaces
git config --global credential.helper store
git clone https://ORG@dev.azure.com/ORG/report-service/_git/report-service
cd report-service
git config --global user.name "Your Name"
git config --global user.email "you@example.com"
```

10. عند طلب Password الصق كلمة المرور.

> ⚠️ من الآن افتح الملفات بالأمر code من الـ Terminal فقط، لا من شجرة الملفات على اليسار. الشجرة تعرض devops-fundamentals-lab، والتعديل فيها لا يصل إلى طلب الدمج.

### 4. التعديل

11. أنشئ فرعًا وافتح ملف البرنامج:

```bash
git checkout -b feature/vehicle-plate
code app/main.py
```

12. داخل validate_report، قبل return errors:

```python
    plate = str(data.get("plate", ""))
    if len(plate) > 10:
        errors.append("plate must be 10 characters or less")
```

13. داخل create_report، قبل "created_at":

```python
        "plate": data.get("plate", "").strip(),
```

14. غيّر رقم الإصدار إلى APP_VERSION = "1.1.0"

15. افتح ملف الاختبارات، وأضف في آخره بعد سطرين فارغين:

```bash
code tests/test_app.py
```

```python
def test_long_plate_is_rejected():
    assert validate_report({"location": "Airport Road", "type": "other", "plate": "12345678901"})
```

16. افحص:

```bash
python -m pytest -q
python -m flake8 app tests
```

> ✓ 7 passed، ولا يطبع flake8 شيئًا

### 5. الحفظ والإرسال

17. تأكد أن التعديل في النسخة الصحيحة:

```bash
pwd
git status
```

> ✓ /workspaces/report-service، وتحتها modified: app/main.py وtests/test_app.py

> ⚠️ إن ظهر nothing to commit فقد عدّلت النسخة الخطأ من الشجرة: افتح الملف بالأمر code وأعد التعديل.

18. استبدل ID برقم مهمتك:

```bash
git add .
git commit -m "Add vehicle plate field #ID"
git push -u origin HEAD
```

### 6. طلب الدمج

19. Repos ثم Pull requests ثم New pull request، من feature/vehicle-plate إلى main.

20. أضف Reviewers، واربط المهمة من Work items to link، ثم Create.

21. المراجع يضغط Approve، ثم أنت Complete واختر Squash commit.

22. فعّل Complete associated work items وDelete branch، ثم Complete merge.

### 7. الإصدار

```bash
cd /workspaces/report-service
git checkout main
git pull
git log --oneline -3
git tag -a v1.1.0 -m "Add vehicle plate field"
git push origin v1.1.0
```

> ✓ Repos > Tags يظهر فيها v1.1.0، والمهمة في Boards حالتها Done

### 8. تمرين التعارض

23. زميلك يعدّل main قبلك (أو نفّذها أنت من المتصفح): Repos ثم Files ثم app/main.py ثم Edit، وفي سطر INCIDENT_TYPES أضف "flood" قبل "other":

```python
INCIDENT_TYPES = {"collision", "breakdown", "obstacle", "flood", "other"}
```

24. Commit بالرسالة Add flood incident type، ثم Commit.

25. في Codespace، ودون git pull، أنشئ فرعًا وعدّل السطر نفسه بإضافة "sandstorm" قبل "other":

```bash
cd /workspaces/report-service
git checkout -b feature/sandstorm-type
code app/main.py
```

```python
INCIDENT_TYPES = {"collision", "breakdown", "obstacle", "sandstorm", "other"}
```

26. احفظ وأرسل:

```bash
git commit -am "Add sandstorm incident type"
git push -u origin HEAD
```

27. افتح طلب دمج من feature/sandstorm-type إلى main، ثم Create.

> ✓ تنبيه تعارض (Conflicts) على app/main.py، والدمج غير ممكن

28. اسحب main إلى فرعك:

```bash
git fetch origin
git merge origin/main
```

> ✓ CONFLICT (content): Merge conflict in app/main.py

29. في app/main.py احذف الأسطر الخمسة بين <<<<<<< و>>>>>>> كلها، واكتب مكانها:

```python
INCIDENT_TYPES = {"collision", "breakdown", "obstacle", "flood", "sandstorm", "other"}
```

> ⚠️ لا تضغط Accept Both Changes: يبقي السطرين، فيلغي الثاني الأول دون أي رسالة خطأ.

30. افحص واحفظ الحل وأرسله:

```bash
python -m pytest -q
python -m flake8 app tests
git add app/main.py
git commit -m "Merge main and resolve conflict"
git push
```

> ✓ 7 passed، ويختفي التعارض من الطلب. أكمل الدمج بـ Squash commit

31. عُد إلى main:

```bash
git checkout main
git pull
```

---

## المعمل الثاني: خط التكامل المستمر

### 1. رمز الوصول (PAT)

1. User settings ثم Personal access tokens ثم New Token.

2. Name: codespace-agent · Expiration: 7 أيام · Scopes: Custom defined ثم Show all scopes ثم Agent Pools: Read & manage.

3. Create، وانسخ الرمز فورًا؛ لا يظهر مرة أخرى.

### 2. الوكيل

4. افتح Terminal جديدًا من علامة +، واستبدل ORG وTOKEN:

```bash
cd /workspaces/report-service
bash scripts/setup-agent.sh https://dev.azure.com/ORG TOKEN
```

> ✓ Listening for Jobs (لا تغلق هذا الـ Terminal)

5. تحقق: Organization settings ثم Agent pools ثم Default ثم Agents، وحالة الوكيل Online.

6. إن توقفت بيئة العمل، أعد تشغيل الوكيل:

```bash
cd ~/azagent && ./run.sh
```

### 3. ملف الخط

7. في Terminal آخر:

```bash
cd /workspaces/report-service
code azure-pipelines.yml
```

8. الصق واحفظ:

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

9. أرسل الملف:

```bash
git add azure-pipelines.yml
git commit -m "Add CI pipeline"
git push
```

### 4. إنشاء الخط

10. Pipelines ثم Create Pipeline ثم Azure Repos Git ثم report-service.

11. Existing Azure Pipelines YAML file، والفرع main، والمسار /azure-pipelines.yml، ثم Continue ثم Run.

12. إن طُلب إذن: View ثم Permit ثم Permit.

> ✓ التشغيل أخضر، وتبويب Tests يعرض 7 Passed

### 5. الكسر والإصلاح

13. في app/main.py غيّر if len(location) < 3: إلى if len(location) < 1:، ثم:

```bash
git add app/main.py
git commit -m "Relax location rule"
git push
```

> ✓ تشغيل جديد وحده (Individual CI)، والنتيجة حمراء

14. افتح Job ثم Run tests، وانزل لآخر السجل: test_short_location_is_rejected و1 failed, 6 passed.

15. أعد السطر إلى < 3، ثم:

```bash
python -m pytest -q
git add app/main.py
git commit -m "Restore location rule"
git push
```

> ✓ التشغيل أخضر مرة أخرى

### 6. التحدي: حماية الفرع

16. Repos ثم Branches، وبجانب main اضغط ⋯ ثم Branch policies.

17. فعّل Require a minimum number of reviewers بقيمة 1، وإن كنت تتدرب وحدك فعّل Allow requestors to approve their own changes.

18. من Build Validation اضغط +، واختر خطك، واجعله Required، ثم Save.

19. جرّب الدفع المباشر إلى main: عدّل سطرًا، واحفظ لقطة، ثم ادفع:

```bash
git checkout main
git pull
echo "# test" >> README.md
git commit -am "Direct push test"
git push
```

> ✓ الدفع مرفوض (rejected) برسالة TF402455

20. أعد نسختك كما كانت:

```bash
git reset --hard origin/main
```

21. جرّب طلب دمج بكود معيب: أنشئ فرعًا، وغيّر < 3 إلى < 1 واحفظ، ثم أرسل:

```bash
git checkout -b feature/broken-rule
code app/main.py
git commit -am "Try relaxing location rule"
git push -u origin HEAD
```

22. افتح طلب دمج من feature/broken-rule إلى main.

> ✓ الخط يفشل على الطلب، وزر Complete معطّل

---

## المعمل الثالث: الخط نفسه على GitHub Actions

### 1. التفعيل

1. افتح نسختك github.com/اسمك/devops-fundamentals-lab ثم تبويب Actions.

2. اضغط I understand my workflows, go ahead and enable them.

### 2. ملف الخط

3. تبويب Code ثم Add file ثم Create new file، والاسم:

```bash
.github/workflows/ci.yml
```

4. الصق:

```yaml
name: CI
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]
jobs:
  build-and-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - name: Install dependencies
        run: python -m pip install -r requirements.txt
      - name: Lint (code quality)
        run: python -m flake8 app tests
      - name: Run tests
        run: python -m pytest
```

5. Commit changes، واختر Commit directly to the main branch، ثم Commit changes.

### 3. التشغيل والمقارنة

6. تبويب Actions، ثم التشغيل الجديد، ثم build-and-test.

> ✓ التشغيل أخضر، وفي Run tests تظهر 6 passed (ميزة رقم المركبة في Azure فقط)

7. قارن بملف Azure: on مقابل trigger، وruns-on مقابل pool، وrun مقابل script، وuses مقابل task. وفي GitHub نحتاج خطوة checkout، أما Azure فيجلب الكود تلقائيًا.
