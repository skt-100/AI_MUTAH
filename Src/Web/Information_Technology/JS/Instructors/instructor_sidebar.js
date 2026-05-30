(async () => {
    const instructorId   = localStorage.getItem("instructorId");
    const instructorName = localStorage.getItem("instructorName");

    if (!instructorId) return;

    // 1. حقن الاسم من localStorage فوراً لمنع الوميض
    const nameEl = document.getElementById("sidebarDrName");
    if (nameEl) nameEl.textContent = instructorName;

    // 2. جلب البيانات الحية من الـ API
    try {
        const res = await fetch(`/api/instructors/${instructorId}`);
        if (res.ok) {
            const result = await res.json();
            if (result.success && result.instructor) {
                const inst = result.instructor;

                if (nameEl && inst.full_name) nameEl.textContent = inst.full_name;

                const rankEl = document.getElementById("sidebarAcademicRank");
                if (rankEl && inst.academic_rank) rankEl.textContent = inst.academic_rank;

                const specEl = document.getElementById("sidebarSpecialization");
                if (specEl && inst.specialization) specEl.textContent = inst.specialization;
            }
        }
    } catch (err) {
        console.error("خطأ أثناء جلب بيانات المحاضر للسايدبار:", err);
    }

    // 3. تحديد الرابط النشط بحسب الصفحة الحالية
    const currentPage = window.location.pathname.split("/").pop();

    if (currentPage === "instructor_dashboard.html" || currentPage === "") {
        document.getElementById("link-instructor_dashboard")?.classList.add("active");
    } else if (currentPage === "instructor_student.html") {
        document.getElementById("link-instructor_student")?.classList.add("active");
    } else if (currentPage === "instructor_notification.html") {
        document.getElementById("link-instructor_notification")?.classList.add("active");
    }

    // 4. تفعيل زر تسجيل الخروج
    const logoutBtn = document.getElementById("instructorLogoutBtn");
    if (logoutBtn) {
        logoutBtn.addEventListener("click", () => {
            localStorage.clear();
            sessionStorage.clear();
            window.location.replace("/");
        });
    }
})();
