// === ─── ربط شاشة تسجيل الدخول وعرض الأخطاء داخل الواجهة بشكل عصري ─── ===

document.addEventListener("DOMContentLoaded", () => {
    const loginForm = document.getElementById("loginForm");
    const userId = document.getElementById("userId");
    const passwordInput = document.getElementById("passwordInput");
    
    // جلب عناصر رسائل الخطأ من الـ HTML
    const userIdError = document.getElementById("userIdError");
    const passwordInputError = document.getElementById("passwordInputError");

    if (!loginForm) return;

    loginForm.onsubmit = function(event) {
        event.preventDefault(); 
        
        const idValue = userId.value.trim();
        const passValue = passwordInput.value.trim();

        // تصفير الأخطاء والتنسيقات السابقة قبل الفحص الجديد
        const resetErrors = () => {
            userId.style.borderColor = "";
            userId.style.boxShadow = "";
            passwordInput.style.borderColor = "";
            passwordInput.style.boxShadow = "";
            userIdError.textContent = "";
            passwordInputError.textContent = "";
        };

        const applyErrorStyle = (element) => {
            element.style.borderColor = "red";
            element.style.boxShadow = "0 0 5px rgba(255, 0, 0, 0.3)";
        };

        resetErrors();
       
        // 1. الفحص المحلي المباشر للحقول الفارغة وعرض الخطأ تحت الحقل فوراً
        if (idValue === "" || passValue === "") {
            if (idValue === "") {
                applyErrorStyle(userId);
                userIdError.textContent = "يرجى إدخال الرقم الجامعي";
            }
            if (passValue === "") {
                applyErrorStyle(passwordInput);
                passwordInputError.textContent = "يرجى إدخال كلمة المرور";
            }
            return; 
        }

        // 2. إرسال البيانات إلى السيرفر
        fetch('/api/student_login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ userId: idValue, password: passValue })
        })
        .then(response => {
            if (!response.ok) {
                return response.json().then(err => {
                    throw new Error(err.message || "البيانات المدخلة غير صحيحة");
                });
            }
            return response.json();
        })
        .then(data => {
            if (data.success) {
                localStorage.clear();
                localStorage.setItem("userId", data.id);
                localStorage.setItem("userName", data.name);
                localStorage.setItem("userRole", data.role);
                window.location.href = data.redirect; 
            }
        })
        .catch(err => {
            console.error("خطأ:", err);
            // حقن الخطأ القادم من السيرفر بشكل نظيف تحت حقل كلمة المرور وتلوين الحقول بالأحمر سفيان الطراونة
            applyErrorStyle(userId);
            applyErrorStyle(passwordInput);
            passwordInputError.textContent = err.message;
        });
    };
});
