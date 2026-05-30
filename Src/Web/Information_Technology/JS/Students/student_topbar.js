// student_topbar.js — منطق إدارة أحداث وتفعيل أزرار الشريط العلوي ذاتياً
(() => {
    // 1. ربط زر تسجيل الخروج وتفعيل الحدث
    const logoutBtn = document.querySelector(".btn-logout");
    if (logoutBtn) {
        logoutBtn.addEventListener("click", () => {
            localStorage.clear();
            window.location.replace("/");
        });
    }

    // 2. ربط زر المساعدة لفتح البوت
    const helpBtn = document.querySelector(".btn-help");
    if (helpBtn) {
        helpBtn.addEventListener("click", () => {
            const chatWidgetWindow = document.getElementById("chatWidgetWindow");
            const chatWidgetInput = document.getElementById("chatWidgetInput");
            
            if (chatWidgetWindow) {
                chatWidgetWindow.classList.add("open");
                if (chatWidgetInput) chatWidgetInput.focus();
            } else {
                alert("يمكنك الاستعانة بالمساعد الأكاديمي الذكي الموجود أسفل الشاشة لمساعدتك.");
            }
        });
    }
})();
