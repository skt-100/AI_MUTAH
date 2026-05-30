document.addEventListener("DOMContentLoaded", async () => {

    const instructorId   = localStorage.getItem("instructorId");
    const instructorName = localStorage.getItem("instructorName");

    // 1. التحقق من أمان الجلسة
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

    // 2. جلب وحقن السايدبار والتوبار
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

    // 3. عرض اسم المحاضر في بانر الترحيب
    const welcomeEl = document.getElementById("welcomeInstructorName");
    if (welcomeEl && instructorName) welcomeEl.textContent = instructorName;

    // 4. جلب إحصائيات الداشبورد الخاصة بالمحاضر
    loadDashboardStats(instructorId);
});


function loadDashboardStats(instructorId) {
    fetch('/api/instructor/dashboard_stats', {
        method:  'POST',
        headers: { 'Content-Type': 'application/json' },
        body:    JSON.stringify({ instructor_id: instructorId })
    })
    .then(res => {
        if (!res.ok) throw new Error("فشل في جلب البيانات");
        return res.json();
    })
    .then(result => {
        if (!result.success) return;

        const { stats, sections } = result;

        // ── البطاقات الأربع ──
        setText("stat-courses",  stats.courses_count);
        setText("stat-sections", stats.sections_count);
        setText("stat-students", stats.total_students);
        setText("stat-requests", stats.pending_requests);

        // ── جدول الشعب ──
        buildSectionsTable(sections, stats.total_students);
    })
    .catch(err => console.error("خطأ في تحميل الداشبورد:", err));
}


function setText(id, value) {
    const el = document.getElementById(id);
    if (el) el.textContent = value ?? "—";
}


function buildSectionsTable(sections, totalStudents) {
    const tbody = document.getElementById("sectionsTableBody");
    const tfoot = document.getElementById("sectionsTableFoot");
    if (!tbody) return;

    if (!sections || sections.length === 0) {
        tbody.innerHTML = `<tr class="st-empty-row"><td colspan="5">لا توجد شعب مخصصة لك حالياً.</td></tr>`;
        return;
    }

    tbody.innerHTML = sections.map((sec, i) => {
        const pct      = sec.capacity > 0 ? Math.round((sec.enrolled_count / sec.capacity) * 100) : 0;
        const barClass = pct >= 100 ? "full" : pct >= 80 ? "almost" : "";
        const delay    = `animation-delay:${0.05 + i * 0.04}s`;

        return `
            <tr style="${delay}">
                <td>
                    <div class="st-course-name">${sec.course_name}</div>
                    <div class="st-course-id">${sec.course_id}</div>
                </td>
                <td><span class="st-section-badge">شعبة ${sec.section_number}</span></td>
                <td><span class="st-count">${sec.enrolled_count}</span></td>
                <td><span class="st-capacity">${sec.capacity}</span></td>
                <td class="st-progress-cell">
                    <div class="st-progress-header">
                        <span class="st-pct ${barClass}">${pct}%</span>
                        <span style="font-size:11px; color:#94a3b8;">${sec.enrolled_count}/${sec.capacity}</span>
                    </div>
                    <div class="st-progress-wrap">
                        <div class="st-progress-bar ${barClass}" style="width:${Math.min(pct,100)}%"></div>
                    </div>
                </td>
            </tr>
        `;
    }).join("");

    if (tfoot) {
        tfoot.innerHTML = `
            <tr>
                <td colspan="2">👨‍🎓 إجمالي الطلاب في جميع الشعب</td>
                <td colspan="3">${totalStudents} طالب</td>
            </tr>
        `;
    }
}
