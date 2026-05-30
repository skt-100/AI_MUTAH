// student_sidebar.js — منطق إدارة وتعبئة القائمة الجانبية بشكل مستقل وتلقائي
(async () => {
    const currentStudentId = localStorage.getItem("userId");
    const currentStudentName = localStorage.getItem("userName");

    // التحقق من وجود الجلسة لمنع الأخطاء البرمجية
    if (!currentStudentId) return;

    try {
        // 1. حقن البيانات النصية الأساسية من الجلسة داخل السايدبار فوراً
        const nameElement = document.getElementById("studentname");
        const idElement = document.getElementById("studentid");

        if (nameElement) nameElement.textContent = currentStudentName;
        if (idElement) idElement.textContent = currentStudentId;

        // 2. جلب بيانات الجنس والصورة الحية للطالب من الـ API
        try {
            const studentDataResponse = await fetch(`/api/students/${currentStudentId}`);
            if (studentDataResponse.ok) {
                const result = await studentDataResponse.json();
                
                if (result.success && result.student) {
                    const student = result.student;
                    let finalProfileSrc;

                    // تطبيق منطق فحص الصورة والجنس المخزنين بالمسار المطلق الجديد
                    if (student.profile_img) {
                        finalProfileSrc = `/Information_Technology/${student.profile_img}`;
                    } else {
                        if (student.gender === 'male') {
                            finalProfileSrc = "/Information_Technology/.img/Profiles/Students/avatar_male.png";
                        } else {
                            finalProfileSrc = "/Information_Technology/.img/Profiles/Students/avatar_female.png";
                        }
                    }

                    // البحث عن عنصر الصورة داخل السايدبار وتحديثه
                    const profileImgElement = document.getElementById("userProfileImg");
                    if (profileImgElement) {
                        profileImgElement.src = finalProfileSrc;
                    }
                }
            }
        } catch (apiError) {
            console.error("خطأ أثناء جلب الصورة الشخصية من الـ API:", apiError);
            // صورة احتياطية عامة بالمسار المطلق في حال فشل السيرفر أو الاتصال
            const profileImgElement = document.getElementById("userProfileImg");
            if (profileImgElement) {
                profileImgElement.src = "/Information_Technology/.img/Profiles/Students/avatar_male.png";
            }
        }

        // 3. تحديد زر القائمة النشط تلقائياً بحسب اسم الصفحة الحالية التي يقف عليها الطالب
        const currentPage = window.location.pathname.split("/").pop();
        
        if (currentPage === "student_dashboard.html" || currentPage === "") {
            document.getElementById("nav-home")?.classList.add("active"); 
        }
        else if (currentPage === "student_registration.html") {
            document.getElementById("nav-register")?.classList.add("active");
        }
        else if (currentPage === "student_honorboard.html") {
            document.getElementById("nav-honor")?.classList.add("active");
        }
        else if (currentPage === "student_instructor.html") {
            document.getElementById("nav-instructors")?.classList.add("active");
        }

    } catch (error) {
        console.error("خطأ أثناء معالجة بيانات القائمة الجانبية:", error);
    }
})();
