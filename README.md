# 🌌 AuraFlow SaaS Boilerplate

بنية تحتية احترافية وهيكل متكامل لبدء وتطوير تطبيقات SaaS البرمجية بسرعة فائقة باستخدام تقنيات الويب الحديثة لعام 2026.

---

## 🛠️ التقنيات الأساسية (Tech Stack)

يتكون القالب من مزيج متجانس يجمع بين أمان واستقرار بيئة الباك إند وسرعة وديناميكية الواجهة الأمامية:

*   **الباك إند (Backend):** [Django](https://www.djangoproject.com/) (نسخة مستقرة).
*   **الواجهة الأمامية (Frontend):** [Vue 3](https://vuejs.org/) (Composition API) مع [Vite](https://vitejs.dev/) كمحرك للبناء السريع.
*   **بروتوكول الربط (Bridge):** [Inertia.js](https://inertiajs.com/) (لربط الباك إند بالفرونت إند مباشرة دون الحاجة لبناء APIs منفصلة).
*   **التنسيق والتصميم (Styling):** [Tailwind CSS v4](https://tailwindcss.com/) مع سمات تصميم مرنة (Design Tokens).
*   **نظام الهوية والأمان (Identity & Auth):** [django-allauth](https://django-allauth.readthedocs.io/en/latest/) (إدارة الحسابات، التحقق، والمصادقة الثنائية).
*   **لوحة الإدارة (Admin Panel):** [django-unfold](https://github.com/unfoldadmin/django-unfold) (لوحة تحكم عصرية تدعم المظهر الداكن).

---

## 📂 هيكلية المجلدات والمشروع (Project Structure)

تم تنظيم الكود وتوزيع الملفات بهيكل نموذجي قابل للنمو (Modular App Structure):

```text
auraflow/
│
├── apps/                    # مجلد التطبيقات الفرعية (Local Apps)
│   └── users/               # تطبيق الهوية والتفضيلات والمستخدمين
│       ├── adapters/        # محولات allauth للتحقق والتسجيل
│       ├── migrations/      # هجرات قاعدة البيانات لنموذج المستخدم
│       ├── tests/           # ملفات الاختبار الخاصة بـ pytest
│       ├── admin.py         # تسجيل النموذج وتخصيص Unfold
│       ├── apps.py          # تعريف التطبيق بالـ namespace الجديد
│       ├── forms.py         # نماذج التحقق من المدخلات (Forms)
│       ├── models.py        # نموذج المستخدم المخصص (CustomUser)
│       ├── urls.py          # روابط الهوية وتسجيل الخروج والتحديث
│       └── views.py         # واجهات التحكم ومستقبلات Inertia
│
├── common/                  # المكونات والأدوات المشتركة للتطبيق
│   ├── middleware.py        # كود وسيط لمشاركة بيانات الجلسة (Inertia Shared Props)
│   ├── logger.py            # سجلات الأحداث الأمنية والـ Audit Trail
│   ├── results.py           # كائن الاستجابة الموحد للخدمات (ServiceResult)
│   └── utils/               # دوال عامة مساعدة (مثل تطبيع البريد)
│
├── core/                    # إعدادات وتكوينات المشروع الرئيسي
│   ├── settings/            # ملفات الإعدادات (base, local, production)
│   ├── urls.py              # مسارات التوجيه الرئيسية وتضمين allauth
│   └── wsgi.py / asgi.py    # بوابات تشغيل الخوادم
│
├── frontend/                # كود الواجهة الأمامية بالكامل (Vue 3 + Vite)
│   ├── src/
│   │   ├── pages/           # صفحات Inertia (Login, Register, Profile)
│   │   ├── layouts/         # القوالب المشتركة (AuthLayout)
│   │   ├── composables/     # الكومبوزابلز (مثل استخراج أخطاء السيرفر)
│   │   ├── types/           # تعريفات الأنواع لـ TypeScript
│   │   └── main.ts          # نقطة دخول التطبيق وتهيئة Inertia
│   └── vite.config.ts       # إعدادات Vite ومزامنتها مع django-vite
│
├── scripts/                 # سكربتات التهيئة والمهام التجريبية
│   └── seed_data.py         # سكربت توليد حسابات تجريبية فورية
│
├── pytest.ini               # تهيئة محرك الاختبارات pytest
├── requirements.txt         # الحزم والمكتبات المطلوبة لـ Python
├── ruff.toml                # إعدادات فحص جودة الكود والتنسيق
└── .pre-commit-config.yaml  # حارس الجودة قبل الـ Git Commit
```

---

## 🔒 حزمة الهوية والأمان (django-allauth Integration)

تم توفير الدعم الكامل لمزايا `django-allauth` وفتح مساراتها بالكامل تحت النطاق `/accounts/` لتسهيل دمج المزايا الأمنية التالية في الـ SaaS الخاص بك:

1.  **المصادقة الثنائية (Two-Factor Authentication / 2FA):** متوفرة وتعمل بكفاءة عبر المسار `/accounts/2fa/` أو `/accounts/mfa/list/` (تولد رمز QR ثنائي الأبعاد بمساعدة حزمة `qrcode` لتطبيقات مثل Google Authenticator).
2.  **تغيير كلمة المرور للداخلين:** متوفرة عبر `/accounts/password/change/`.
3.  **استعادة الحساب وكلمات المرور المنسية:** متوفرة وتدعم إرسال روابط الاستعادة عبر البريد من خلال المسار `/accounts/password/reset/`.
4.  **ربط الحسابات الاجتماعية (Social Connections):** إمكانية ربط حسابات Google أو GitHub وإدارتها عبر المسار `/accounts/social/connections/`.

---

## 🚀 خطوات التهيئة والتشغيل المحلي (Setup & Run Guide)

### 1. إعداد البيئة البرمجية وتثبيت المكتبات
```bash
# إنشاء بيئة افتراضية لـ Python
python -m venv .venv

# تفعيل البيئة (Windows)
.venv\Scripts\activate
# تفعيل البيئة (Linux / macOS)
source .venv/bin/activate

# تثبيت الحزم المطلوبة
pip install -r requirements.txt

# تثبيت متصفحات Playwright المطلوبة للاختبارات
playwright install
```

### 2. تجهيز قاعدة البيانات والبيانات التجريبية
```bash
# تشغيل هجرات قاعدة البيانات
python manage.py migrate

# تشغيل سكربت التهيئة الفوري لتوليد حسابات للتجربة
python manage.py runscript seed_data
```
> **الحسابات التجريبية المنشأة:**
> *   **حساب المدير الخارق:** `admin@auraflow.com` | كلمة المرور: `AdminPass123!`
> *   **حساب المستخدم العادي:** `user@auraflow.com` | كلمة المرور: `UserPass123!`

### 3. تشغيل خوادم التطوير
لتشغيل التطبيق، تحتاج إلى تشغيل خادم الباك إند وخادم الفرونت إند بالتوازي:

```bash
# تشغيل خادم دجانغو للباك إند (في نافذة طرفية أولى)
python manage.py runserver

# تشغيل خادم Vite للفرونت إند (في نافذة طرفية ثانية)
npm run dev
```

---

## 🧪 فحص جودة الكود والاختبارات (QA & Testing)

### 1. جودة وتنسيق الكود (Ruff & Pre-Commit)
يحتوي القالب على حارس جودة مؤتمت لمنع دخول كود غير منظم:
```bash
# تفعيل خطافات pre-commit قبل الكوميت
pre-commit install

# لتشغيل الفحص التلقائي والتنسيق يدوياً في أي وقت
ruff check --fix
ruff format
```

### 2. تشغيل الاختبارات المؤتمتة (Pytest & Playwright)
يحتوي المشروع على اختبارات شاملة للباك إند وتكامل الـ E2E:
```bash
# لتشغيل كامل بيئة الاختبارات
pytest
```
*   تقوم الاختبارات بفحص نموذج المستخدم المخصص وصحة الصلاحيات.
*   تقوم واجهات Playwright بتشغيل متصفح حقيقي بالخلفية لفتح صفحة التسجيل والدخول وتغيير التفضيلات الشخصية (Theme) والتأكد من تطبيق السمة داكن/فاتح بصرياً والتأكد من نجاح تسجيل الخروج.
