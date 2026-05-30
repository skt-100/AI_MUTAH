(async () => {
    const instructorId   = localStorage.getItem("instructorId");
    const instructorName = localStorage.getItem("instructorName");

    // 1. حقن الاسم من localStorage فوراً لمنع الوميض
    const nameEl = document.getElementById("topbarDrName");
    if (nameEl && instructorName) nameEl.textContent = instructorName;

    if (!instructorId) return;

    // 2. جلب الرتبة الأكاديمية من الـ API
    try {
        const res = await fetch(`/api/instructor/topbar/${instructorId}`);
        if (res.ok) {
            const result = await res.json();
            if (result.success && result.instructor) {
                const inst = result.instructor;

                if (nameEl && inst.full_name) nameEl.textContent = inst.full_name;

                const rankEl = document.getElementById("topbarAcademicRank");
                if (rankEl && inst.academic_rank) rankEl.textContent = inst.academic_rank;
            }
        }
    } catch (err) {
        console.error("خطأ أثناء جلب بيانات المحاضر للتوب بار:", err);
    }
})();
