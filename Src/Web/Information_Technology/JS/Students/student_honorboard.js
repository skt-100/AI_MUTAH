// student_honorboard.js — جلب بيانات لوحة الشرف وعرضها مع المكونات المشتركة والفلترة
document.addEventListener("DOMContentLoaded", async () => {

    const currentStudentId = localStorage.getItem("userId");

    // 1. التحقق من أمان الجلسة
    if (!currentStudentId) {
        alert("جلسة غير صالحة، يرجى تسجيل الدخول أولاً");
        window.location.href = "/";
        return;
    }

    // 2. جلب ملفات الواجهة المشتركة (التوب بار والسايدبار) وحقنها برمجياً لتعمل الـ Modules ذاتياً
    const inject = (container, html) => {
        container.innerHTML = html;
        container.querySelectorAll('script').forEach(old => {
            const s = document.createElement('script');
            [...old.attributes].forEach(a => s.setAttribute(a.name, a.value));
            s.textContent = old.textContent;
            old.replaceWith(s);
        });
    };

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

    // ربط الجداول بمفاتيح التخصص بناءً على الـ DOM الحالي
    const tables = {
        "هندسة البرمجيات":              document.getElementById("se-students"),
        "علم الحاسوب":                  document.getElementById("cs-students"),
        "الذكاء الاصطناعي وعلم البيانات": document.getElementById("ai-students"),
        "نظم معلومات حاسوبية":          document.getElementById("cis-students"),
        "أمن معلومات":                  document.getElementById("cyber-students")
    };

    // رسالة الجدول الفارغ
    const emptyRow = () =>
        `<tr><td colspan="4">🔍 لا توجد معدلات متأهلة في هذا التخصص حالياً.</td></tr>`;

    // 3. جلب البيانات من الـ API عبر مسار نسبي مباشر للسيرفر
    fetch('/api/student_honorboard')
        .then(res => {
            if (!res.ok) throw new Error("فشل الاتصال بالسيرفر");
            return res.json();
        })
        .then(result => {
            // تنظيف الجداول أولاً
            Object.values(tables).forEach(tbody => {
                if (tbody) tbody.innerHTML = "";
            });

            if (result.success && result.data.length > 0) {
                result.data.forEach(student => {
                    const tbody = tables[student.specialization];
                    if (!tbody) return;

                    // أيقونة الميدالية للمراكز الثلاثة الأولى
                    let rankDisplay = student.student_rank;
                    if      (student.student_rank === 1) rankDisplay = "🥇 1";
                    else if (student.student_rank === 2) rankDisplay = "🥈 2";
                    else if (student.student_rank === 3) rankDisplay = "🥉 3";

                    const row = document.createElement("tr");
                    row.innerHTML = `
                        <td>${rankDisplay}</td>
                        <td>${student.full_name}</td>
                        <td>${student.completed_hours} ساعة</td>
                        <td style="font-weight: bold; color: #C9963A;">${parseFloat(student.gpa).toFixed(2)}</td>
                    `;
                    tbody.appendChild(row);
                });
            }

            // عرض رسالة الجدول الفارغ لكل تخصص لم تصله بيانات من الـ MySQL
            Object.values(tables).forEach(tbody => {
                if (tbody && tbody.innerHTML === "") {
                    tbody.innerHTML = emptyRow();
                }
            });
        })
        .catch(err => console.error("خطأ أثناء جلب لوحة الشرف:", err));

    // 4. منطق الفلترة الفورية بالبحث
    const searchInput = document.getElementById("searchInput");
    if (!searchInput) return;

    searchInput.addEventListener("input", () => {
        const query = searchInput.value.trim().toLowerCase();

        document.querySelectorAll(".table-container").forEach(container => {
            const tbody     = container.querySelector("tbody");
            const title     = container.previousElementSibling;
            const rows      = tbody.querySelectorAll("tr");
            let   visible   = 0;

            rows.forEach(row => {
                const name = row.cells[1] ? row.cells[1].textContent.toLowerCase() : "";
                const show = !query || name.includes(query);
                row.style.display = show ? "" : "none";

                // أنيميشن ظهور ناعم للصفوف المفلترة
                if (show) {
                    row.style.opacity = "0";
                    setTimeout(() => {
                        row.style.transition = "opacity 0.25s ease";
                        row.style.opacity    = "1";
                    }, 10);
                    visible++;
                }
            });

            // إخفاء كامل التخصص إذا لم يطابق اسم البحث أي صف بداخل الجدول
            const hide = visible === 0 && query !== "";
            container.style.display         = hide ? "none" : "";
            if (title) title.style.display  = hide ? "none" : "";
        });
    });
});
