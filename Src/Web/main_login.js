document.addEventListener("DOMContentLoaded", () => {
    const facultyNameEl = document.getElementById("facultyName");
    const storedName = localStorage.getItem("selectedFaculty");

    if (storedName && facultyNameEl) {
        facultyNameEl.textContent = storedName;
    }

    // ربط كروت الأدوار بمسارات الملفات الاستاتيكية الصحيحة عبر الفلاسك
    const studentCard  = document.querySelector(".card-student");
    const teacherCard  = document.querySelector(".card-teacher");
    const deanCard     = document.querySelector(".card-dean");
    const adminCard    = document.querySelector(".card-admin");

    // توجيه الطالب إلى شاشة الدخول الخاصة بالطلاب (الموجودة في المجلد الفرعي)
    if (studentCard) {
        studentCard.setAttribute("href", "/Information_Technology/HTML/Students/student_login.html");
    }

    // توجيه المدرس (يمكنك تعديل المسار لاحقاً عند بناء صفحة دخول المدرسين)
    if (teacherCard) {
        teacherCard.setAttribute("href", "/Information_Technology/HTML/Instructors/instructor_login.html");
    }

    // توجيه العميد
    if (deanCard) {
        deanCard.setAttribute("href", "/Information_Technology/HTML/Dean/dean_login.html");
    }

    // توجيه المسؤول (الأدمن)
    if (adminCard) {
        adminCard.setAttribute("href", "/Information_Technology/HTML/Admin/admin_login.html");
    }
});
