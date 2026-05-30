// student_dashboard.js — منطق لوحة تحكم الطالب وربط البيانات الحية
document.addEventListener("DOMContentLoaded", async () => {

    const currentStudentId   = localStorage.getItem("userId");
    const currentStudentName = localStorage.getItem("userName");

    // 1. التحقق من أمان الجلسة
    if (!currentStudentId) {
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

    // 2. جلب ملفات الواجهة المشتركة (التوب بار والسايدبار) وحقنها برمجياً
    try {
        const topbarHeader = document.querySelector(".topbar");
        const sidebarAside = document.querySelector(".sidebar");

        const [topbarHtml, sidebarHtml] = await Promise.all([
            fetch('/Information_Technology/HTML/Students/student_topbar.html').then(r => r.text()),
            fetch('/Information_Technology/HTML/Students/student_sidebar.html').then(r => r.text())
        ]);

        if (topbarHeader) inject(topbarHeader, topbarHtml);
        if (sidebarAside) inject(sidebarAside, sidebarHtml);

    } catch (error) {
        console.error("خطأ أثناء جلب وتحديث المكونات المشتركة:", error);
    }

    // 3. تعبئة اسم الطالب والتاريخ في شريط الميتا بالواجهة الرئيسية
    const metaNameElem = document.getElementById("metaName");
    if (metaNameElem && currentStudentName) {
        metaNameElem.textContent = currentStudentName;
    }

    const metaDateElem = document.getElementById("metaDate");
    if (metaDateElem) {
        metaDateElem.textContent = new Date().toLocaleDateString("ar-JO", {
            year: "numeric", month: "long", day: "numeric"
        });
    }

    // 4. دالة لاقتصاص الأسماء المركبة للترحيب بالطالب
    const getSmartFirstName = (fullName) => {
        if (!fullName) return "الطالب";
        const nameParts = fullName.trim().split(/\s+/);
        const compoundPrefixes = ["عبد", "أبو", "أم", "صلاح", "نور", "سيف", "بهاء", "ذو", "علاء", "شمس", "جمال", "كمال", "محمد"];
        if (compoundPrefixes.includes(nameParts[0]) && nameParts.length > 1) {
            return `${nameParts[0]} ${nameParts[1]}`;
        }
        return nameParts[0];
    };

    const welcomeElem = document.getElementById("welcomeStudentName");
    if (welcomeElem && currentStudentName) {
        welcomeElem.textContent = getSmartFirstName(currentStudentName);
    }

    // 5. جلب إحصائيات البطاقات الحية عبر مسار نسبي مباشر للسيرفر
    fetch('/api/student_dashboard_info', {
        method:  'POST',
        headers: { 'Content-Type': 'application/json' },
        body:    JSON.stringify({ student_id: currentStudentId })
    })
    .then(res => {
        if (!res.ok) throw new Error("فشل في جلب بيانات ملخص الحساب");
        return res.json();
    })
    .then(result => {
        if (!result.success) return;
        const info = result.data;

        const set = (id, val) => {
            const el = document.getElementById(id);
            if (el) el.textContent = val;
        };

        // توزيع البيانات الحية القادمة من قاعدة البيانات على الكروت
        set("studentgpa",      info.gpa);
        set("completedhours",  info.completed_hours);
        set("academicyear",    info.academic_year);
        set("pendingrequests", info.pending_count);
        set("approvedrequests",info.enrolled_count);
        set("enrolledhours",   info.enrolled_hours ?? "—");
        set("passedcourses",   info.passed_courses ?? "—");
        set("remaininghours",  Math.max(0, 132 - info.completed_hours));
    })
    .catch(err => console.error("خطأ أثناء تحديث ملخص الحساب:", err));

    // 6. جلب جدول المواد المسجلة للفصل الحالي عبر مسار نسبي مباشر
    fetch('/api/student_dashboard_courses', {
        method:  'POST',
        headers: { 'Content-Type': 'application/json' },
        body:    JSON.stringify({ student_id: currentStudentId })
    })
    .then(res => {
        if (!res.ok) throw new Error("فشل في جلب المواد المسجلة");
        return res.json();
    })
    .then(result => {
        const tbody = document.getElementById("studentCoursesTable");
        const badge = document.getElementById("coursesCount");
        if (!result.success || !tbody) return;

        const courses = result.courses;

        if (badge) badge.textContent = `${courses.length} مواد مسجلة`;

        if (courses.length === 0) {
            tbody.innerHTML = `<tr><td colspan="6" style="text-align:center;">لا يوجد مواد مسجلة للفصل الحالي</td></tr>`;
            return;
        }

        // بناء صفوف الجدول ديناميكياً بناءً على بيانات الـ MySQL
        tbody.innerHTML = courses.map(c => `
            <tr>
                <td>${c.course_id}</td>
                <td>${c.course_name}</td>
                <td>${c.credit_hours}</td>
                <td>${c.instructor_name}</td>
                <td>${c.days} — ${c.time}</td>
                <td>${c.room}</td>
            </tr>
        `).join("");
    })
    .catch(err => console.error("خطأ أثناء جلب المواد المسجلة:", err));

    // 7. جلب الإشعارات الخاصة بالطالب
    fetch('/api/student_dashboard_notifications', {
        method:  'POST',
        headers: { 'Content-Type': 'application/json' },
        body:    JSON.stringify({ student_id: currentStudentId })
    })
    .then(res => res.json())
    .then(result => {
        if (!result.success) return;
        renderPrivateNotifications(result.private);
    })
    .catch(err => console.error("خطأ أثناء جلب الإشعارات:", err));
});

function renderPrivateNotifications(notifications) {
    const badge = document.getElementById("privateBadge");
    const body  = document.getElementById("privateBody");
    if (!body) return;

    const count = notifications.length;
    if (badge) badge.textContent = `${count} إشعار`;

    if (count === 0) {
        body.innerHTML = `
            <div class="noti-empty-state">
                <div class="empty-check-icon">✓</div>
                <p class="empty-text">لا توجد إشعارات خاصة بالطالب</p>
            </div>`;
        return;
    }

    const icons = { 'وقت': '🕐', 'قاعة': '🏫', 'مدرس': '👨‍🏫', 'يوم': '📅' };

    body.classList.add("has-items");
    body.innerHTML = notifications.map(n => `
        <div class="noti-item">
            <div class="noti-item-header">
                <span class="noti-item-type">
                    ${icons[n.change_type] || '📌'} تغيير ${n.change_type} — ${n.course_name}
                </span>
                <span class="noti-item-date">${n.sent_at}</span>
            </div>
            <p class="noti-item-text">${n.message}</p>
        </div>
    `).join('');
}
