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
        const topbarHeader = document.querySelector(".topbar");
        const sidebarAside = document.querySelector(".sidebar");

        const [topbarHtml, sidebarHtml] = await Promise.all([
            fetch('/Information_Technology/HTML/Instructors/instructor_topbar.html').then(r => r.text()),
            fetch('/Information_Technology/HTML/Instructors/instructor_sidebar.html').then(r => r.text())
        ]);

        if (topbarHeader) inject(topbarHeader, topbarHtml);
        if (sidebarAside) inject(sidebarAside, sidebarHtml);

    } catch (error) {
        console.error("خطأ أثناء جلب وتحديث المكونات المشتركة:", error);
    }

    // 3. عرض اسم المحاضر في بانر الترحيب
    const navDrNameEl = document.getElementById("navDrName");
    if (navDrNameEl && instructorName) navDrNameEl.textContent = instructorName;

    const courseSelect  = document.getElementById("courseSelect");
    const sectionSelect = document.getElementById("sectionSelect");
    const tableBody     = document.getElementById("tableBody");
    const tableTitle    = document.getElementById("tableTitle");
    const saveAllBtn    = document.getElementById("saveAllBtn");

    // بناء حاوية أزرار التبويب ديناميكياً
    const cardSection  = document.querySelector(".white-card");
    const tabContainer = document.createElement("div");
    tabContainer.style.cssText = "display: flex; gap: 15px; margin-top: 20px; border-top: 1px solid #e2e8f0; padding-top: 20px;";
    tabContainer.innerHTML = `
        <button type="button" id="btnModeAttendance" class="tab-button" style="background-color: #0284c7;">📅 إدارة الحضور والغياب</button>
        <button type="button" id="btnModeGrades"     class="tab-button" style="background-color: #64748b;">📝 رصد العلامات والأعمال</button>
    `;
    cardSection.appendChild(tabContainer);

    let currentMode        = "attendance";
    let studentsCachedData = [];

    document.getElementById("btnModeAttendance").addEventListener("click", () => {
        currentMode = "attendance";
        document.getElementById("btnModeAttendance").style.backgroundColor = "#0284c7";
        document.getElementById("btnModeGrades").style.backgroundColor     = "#64748b";
        renderTableStructure();
    });

    document.getElementById("btnModeGrades").addEventListener("click", () => {
        currentMode = "grades";
        document.getElementById("btnModeAttendance").style.backgroundColor = "#64748b";
        document.getElementById("btnModeGrades").style.backgroundColor     = "#7c3aed";
        renderTableStructure();
    });

    // 4. جلب المساقات بناءً على instructor_id من قاعدة البيانات
    fetch('/api/instructor/courses', {
        method:  'POST',
        headers: { 'Content-Type': 'application/json' },
        body:    JSON.stringify({ instructor_id: instructorId })
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            data.courses.forEach(c => {
                const opt = document.createElement("option");
                opt.value     = c.course_id;
                opt.innerText = `${c.course_id} - ${c.course_name}`;
                courseSelect.appendChild(opt);
            });
        }
    })
    .catch(err => console.error("خطأ أثناء جلب المساقات:", err));

    // 5. جلب الشعب عند اختيار المساق
    courseSelect.addEventListener("change", () => {
        sectionSelect.innerHTML    = '<option value="">-- اختر الشعبة --</option>';
        tableBody.innerHTML        = `<tr><td style="text-align:center; padding:30px; color:#7f8c8d;">💡 يرجى تحديد الشعبة المخصصة لبناء كشوفات الطلاب.</td></tr>`;
        studentsCachedData         = [];
        if (!courseSelect.value) return;

        fetch('/api/instructor/sections', {
            method:  'POST',
            headers: { 'Content-Type': 'application/json' },
            body:    JSON.stringify({ instructor_id: instructorId, course_id: courseSelect.value })
        })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                data.sections.forEach(s => {
                    const opt = document.createElement("option");
                    opt.value     = s.section_id;
                    opt.innerText = `شعبة ${s.section_number}`;
                    sectionSelect.appendChild(opt);
                });
            }
        })
        .catch(err => console.error("خطأ أثناء جلب الشعب:", err));
    });

    // 6. جلب قائمة الطلاب عند اختيار الشعبة
    sectionSelect.addEventListener("change", () => {
        if (!sectionSelect.value) {
            tableBody.innerHTML = `<tr><td style="text-align:center; padding:30px; color:#7f8c8d;">💡 يرجى تحديد الشعبة المخصصة لبناء كشوفات الطلاب.</td></tr>`;
            return;
        }
        fetchStudentsData();
    });

    function fetchStudentsData() {
        tableBody.innerHTML = `<tr><td style="text-align:center; padding:30px; color:#64748b;">⏳ جاري إعداد وتجميع البيانات من قاعدة البيانات...</td></tr>`;

        fetch('/api/instructor/students_list', {
            method:  'POST',
            headers: { 'Content-Type': 'application/json' },
            body:    JSON.stringify({ section_id: sectionSelect.value })
        })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                studentsCachedData = data.students;
                renderTableStructure();
            }
        })
        .catch(err => console.error("خطأ أثناء جلب الطلاب:", err));
    }

    // 7. بناء هيكل الجدول بناءً على الوضع المختار
    function renderTableStructure() {
        const thead = document.querySelector("#studentsTable thead");
        tableBody.innerHTML = "";

        if (studentsCachedData.length === 0) {
            tableBody.innerHTML = `<tr><td style="text-align:center; padding:30px; color:#64748b;">🔍 لا يوجد طلاب مسجلين في هذه الشعبة حالياً.</td></tr>`;
            if (thead) thead.innerHTML = "";
            return;
        }

        if (currentMode === "attendance") {
            tableTitle.innerHTML = "📋 لوحة التحكم بالغيابات <span style='color:#0284c7; font-size:14px;'>(حفظ مباشر لجدول attendance)</span>";
            thead.innerHTML = `
                <tr>
                    <th>الرقم الجامعي</th>
                    <th>اسم الطالب</th>
                    <th>الإجراء السريع</th>
                    <th>إجمالي الغيابات الحالي</th>
                </tr>
            `;
            studentsCachedData.forEach(st => {
                const tr = document.createElement("tr");
                tr.dataset.studentId = st.student_id;
                tr.innerHTML = `
                    <td><strong>${st.student_id}</strong></td>
                    <td>${st.full_name}</td>
                    <td><button type="button" class="absent-trigger-btn" onclick="addAbsentCount(this)">🔴 رصد غياب اليوم</button></td>
                    <td><input type="number" class="table-counter-input" value="${st.absences_count}" min="0" max="15"></td>
                `;
                tableBody.appendChild(tr);
            });
        } else {
            tableTitle.innerHTML = "📝 لوحة رصد درجات الفصل <span style='color:#7c3aed; font-size:14px;'>(حفظ مباشر لجدول grades)</span>";
            thead.innerHTML = `
                <tr>
                    <th>الرقم الجامعي</th>
                    <th>اسم الطالب المعتمد</th>
                    <th>المشاركة (20)</th>
                    <th>المنتصف (30)</th>
                    <th>النهائي (50)</th>
                    <th>المجموع الكامل (100)</th>
                </tr>
            `;
            studentsCachedData.forEach(st => {
                const total = Number(st.participation) + Number(st.midterm) + Number(st.final);
                const tr = document.createElement("tr");
                tr.dataset.studentId = st.student_id;
                tr.innerHTML = `
                    <td><strong>${st.student_id}</strong></td>
                    <td>${st.full_name}</td>
                    <td><input type="number" class="grade-input part" value="${st.participation}" min="0" max="20" oninput="liveSumTotal(this)"></td>
                    <td><input type="number" class="grade-input mid"  value="${st.midterm}"       min="0" max="30" oninput="liveSumTotal(this)"></td>
                    <td><input type="number" class="grade-input fin"  value="${st.final}"         min="0" max="50" oninput="liveSumTotal(this)"></td>
                    <td class="row-total" style="font-weight:700; color:#0f172a; background-color:#f8fafc;">${total.toFixed(2)}</td>
                `;
                tableBody.appendChild(tr);
            });
        }
    }

    // 8. حفظ الكشوفات إلى قاعدة البيانات
    saveAllBtn.addEventListener("click", () => {
        if (!sectionSelect.value) {
            alert("يرجى تحديد المساق والشعبة المطلوبة أولاً قبل عملية الحفظ.");
            return;
        }

        const rows    = tableBody.querySelectorAll("tr");
        const records = [];

        rows.forEach(row => {
            const sId = row.dataset.studentId;
            if (!sId) return;

            const original = studentsCachedData.find(st => st.student_id == sId);

            let absences  = original ? original.absences_count : 0;
            let part      = original ? original.participation  : 0;
            let midterm   = original ? original.midterm        : 0;
            let finalGrad = original ? original.final          : 0;

            if (currentMode === "attendance") {
                absences = parseInt(row.querySelector(".table-counter-input").value) || 0;
            } else {
                part      = parseFloat(row.querySelector(".grade-input.part").value) || 0;
                midterm   = parseFloat(row.querySelector(".grade-input.mid").value)  || 0;
                finalGrad = parseFloat(row.querySelector(".grade-input.fin").value)  || 0;
            }

            records.push({
                student_id:     sId,
                absences_count: absences,
                participation:  part,
                midterm:        midterm,
                final:          finalGrad
            });
        });

        fetch('/api/instructor/save_records', {
            method:  'POST',
            headers: { 'Content-Type': 'application/json' },
            body:    JSON.stringify({ section_id: sectionSelect.value, mode: currentMode, records })
        })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                alert(`🎉 تم حفظ كشوفات جدول الـ ${currentMode === 'attendance' ? 'attendance' : 'grades'} بنجاح!`);
                fetchStudentsData();
            } else {
                alert("❌ فشل الحفظ: " + data.message);
            }
        })
        .catch(err => alert("تعذر الاتصال بالسيرفر: " + err));
    });
});

// دالة رصد الزيادة الفورية للغياب
function addAbsentCount(btn) {
    const input = btn.closest("tr").querySelector(".table-counter-input");
    input.value = (parseInt(input.value) || 0) + 1;
}

// دالة الجمع الحركي للعلامات
function liveSumTotal(input) {
    const row     = input.closest("tr");
    const part    = parseFloat(row.querySelector(".grade-input.part").value) || 0;
    const midterm = parseFloat(row.querySelector(".grade-input.mid").value)  || 0;
    const fin     = parseFloat(row.querySelector(".grade-input.fin").value)  || 0;
    row.querySelector(".row-total").innerText = (part + midterm + fin).toFixed(2);
}
