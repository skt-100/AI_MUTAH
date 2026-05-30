const loginForm     = document.getElementById("loginForm");
const userId        = document.getElementById("userId");
const passwordInput = document.getElementById("passwordInput");
const userIdError   = document.getElementById("userIdError");
const passError     = document.getElementById("passwordInputError");


loginForm.onsubmit = function(event) {
    event.preventDefault();

    const idVal   = userId.value.trim();
    const passVal = passwordInput.value.trim();

    // ── التحقق من الحقول ──────────────────────────────────
    userIdError.textContent = "";
    passError.textContent   = "";

    if (!idVal) {
        userIdError.textContent = "الرقم الوظيفي مطلوب";
        userId.classList.add("input-error");
        return;
    }

    if (!passVal) {
        passError.textContent = "كلمة المرور مطلوبة";
        passwordInput.classList.add("input-error");
        return;
    }

    // ── إرسال البيانات ─────────────────────────────────────
    // جدول instructors: instructor_id, password
    fetch('/api/instructor_login', {
        method:  'POST',
        headers: { 'Content-Type': 'application/json' },
        body:    JSON.stringify({ instructor_id: idVal, password: passVal })
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            localStorage.clear();
            localStorage.setItem("instructorId",   data.id);
            localStorage.setItem("instructorName", data.name);
            localStorage.setItem("userRole",       "admin");
            window.location.href = data.redirect;
        } else {
            passError.textContent = data.message || "البيانات غير صحيحة";
            passwordInput.classList.add("input-error");
        }
    })
    .catch(() => {
        passError.textContent = "تعذّر الاتصال بالسيرفر";
    });
};
