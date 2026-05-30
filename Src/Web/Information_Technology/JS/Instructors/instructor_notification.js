document.addEventListener("DOMContentLoaded", async () => {

    const instructorId   = localStorage.getItem("instructorId");
    const instructorName = localStorage.getItem("instructorName");

    // 1. التحقق من الجلسة
    if (!instructorId) {
        alert("جلسة غير صالحة، يرجى تسجيل الدخول أولاً");
        window.location.href = "/";
        return;
    }

    const inject = (container, html) => {
        container.innerHTML = html;
        container.querySelectorAll('script').forEach(old => {
            const s = document.createElement('script');
            [...old.attributes].forEach(a => s.setAttribute(a.name, a.value));
            s.textContent = old.textContent;
            old.replaceWith(s);
        });
    };

    // 2. حقن التوبار والسايدبار
    try {
        const [topbarHtml, sidebarHtml] = await Promise.all([
            fetch('/Information_Technology/HTML/Instructors/instructor_topbar.html').then(r => r.text()),
            fetch('/Information_Technology/HTML/Instructors/instructor_sidebar.html').then(r => r.text())
        ]);
        inject(document.querySelector(".topbar"),  topbarHtml);
        inject(document.querySelector(".sidebar"), sidebarHtml);
    } catch (err) {
        console.error("خطأ أثناء جلب المكونات المشتركة:", err);
    }

    // ── عناصر النموذج ──
    const courseSelect = document.getElementById("courseSelect");
    const sectionSelect = document.getElementById("sectionSelect");
    const changeType    = document.getElementById("changeType");
    const newValue      = document.getElementById("newValue");
    const fieldHint     = document.getElementById("fieldHint");
    const submitBtn     = document.getElementById("submitBtn");
    const btnText       = document.getElementById("btnText");
    const btnSpinner    = document.getElementById("btnSpinner");
    const resultBox     = document.getElementById("resultBox");

    const hints = {
        'وقت':  { placeholder: 'مثال: 10:00',      hint: 'أدخل الوقت بصيغة HH:MM' },
        'قاعة': { placeholder: 'مثال: IT_Lab 02',  hint: 'أدخل اسم القاعة كما هو في النظام' },
        'مدرس': { placeholder: 'مثال: 3',           hint: '⚠️ أدخل رقم ID المدرس وليس اسمه' },
        'يوم':  { placeholder: 'مثال: الاثنين',     hint: 'أدخل اسم اليوم بالعربي' },
    };

    // 3. جلب مواد المحاضر
    fetch('/api/instructor/courses', {
        method:  'POST',
        headers: { 'Content-Type': 'application/json' },
        body:    JSON.stringify({ instructor_id: instructorId })
    })
    .then(r => r.json())
    .then(data => {
        if (!data.success) return;
        data.courses.forEach(c => {
            const opt = document.createElement("option");
            opt.value     = c.course_id;
            opt.textContent = `${c.course_name}`;
            courseSelect.appendChild(opt);
        });
    })
    .catch(err => console.error("خطأ في جلب المواد:", err));

    // 4. جلب الشعب عند اختيار المادة
    courseSelect.addEventListener("change", () => {
        sectionSelect.innerHTML  = '<option value="">— اختر الشعبة —</option>';
        sectionSelect.disabled   = true;
        checkFormReady();

        if (!courseSelect.value) return;

        fetch('/api/instructor/sections', {
            method:  'POST',
            headers: { 'Content-Type': 'application/json' },
            body:    JSON.stringify({ instructor_id: instructorId, course_id: courseSelect.value })
        })
        .then(r => r.json())
        .then(data => {
            if (!data.success) return;
            data.sections.forEach(s => {
                const opt = document.createElement("option");
                opt.value       = s.section_id;
                opt.textContent = `شعبة ${s.section_number}`;
                sectionSelect.appendChild(opt);
            });
            sectionSelect.disabled = false;
        })
        .catch(err => console.error("خطأ في جلب الشعب:", err));
    });

    // 5. تحديث الـ hint والـ placeholder عند تغيير النوع
    changeType.addEventListener("change", () => {
        const type = changeType.value;
        if (hints[type]) {
            newValue.placeholder = hints[type].placeholder;
            fieldHint.textContent = hints[type].hint;
            newValue.disabled     = false;
        } else {
            newValue.placeholder  = "اختر نوع التغيير أولاً";
            fieldHint.textContent = "";
            newValue.disabled     = true;
        }
        newValue.value = "";
        checkFormReady();
    });

    sectionSelect.addEventListener("change", checkFormReady);
    newValue.addEventListener("input", checkFormReady);

    function checkFormReady() {
        const ready = sectionSelect.value && changeType.value && newValue.value.trim();
        submitBtn.disabled = !ready;
    }

    // 6. إرسال الإشعار
    submitBtn.addEventListener("click", async () => {
        const section_id    = sectionSelect.value;
        const change_type   = changeType.value;
        const new_value_val = newValue.value.trim();

        if (!section_id || !change_type || !new_value_val) return;

        btnText.textContent     = "جاري الإرسال...";
        btnSpinner.style.display = "inline-block";
        submitBtn.disabled       = true;
        resultBox.className      = "result-box";
        resultBox.style.display  = "none";

        try {
            const res  = await fetch('/api/instructor/notify', {
                method:  'POST',
                headers: { 'Content-Type': 'application/json' },
                body:    JSON.stringify({
                    instructor_id: instructorId,
                    section_id,
                    change_type,
                    new_value: new_value_val
                })
            });
            const data = await res.json();

            if (data.success) {
                resultBox.className = "result-box success";
                resultBox.innerHTML = `
                    ✅ ${data.message}<br>
                    تم الإرسال: <strong>${data.sent ?? 0}</strong> طالب |
                    فشل: <strong>${data.failed ?? 0}</strong>
                `;
                // إعادة تعيين النموذج
                sectionSelect.value = "";
                changeType.value    = "";
                newValue.value      = "";
                newValue.placeholder = "اختر نوع التغيير أولاً";
                newValue.disabled   = true;
                fieldHint.textContent = "";
            } else {
                resultBox.className = "result-box error";
                resultBox.innerHTML = `❌ ${data.message}`;
            }

        } catch {
            resultBox.className = "result-box error";
            resultBox.innerHTML = "❌ تعذّر الاتصال بالسيرفر";
        }

        btnText.textContent      = "🚀 تطبيق التغيير وإرسال الإشعارات";
        btnSpinner.style.display = "none";
        submitBtn.disabled       = false;
        checkFormReady();
    });
});
