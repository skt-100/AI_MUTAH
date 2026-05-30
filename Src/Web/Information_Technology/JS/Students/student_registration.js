// === ─── منطق شاشة التسجيل وسحب وإضافة المواد الحية بجامعة مؤتة ─── ===

document.addEventListener("DOMContentLoaded", async () => {
    // جلب الرقم الجامعي من الـ LocalStorage لتأمين الجلسة
    const currentStudentId = localStorage.getItem("userId");

    if (!currentStudentId) {
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

    // ── جلب وعرض طلبات الانتظار ──────────────────────────────────────────
    function loadPendingRequests(studentId) {
        fetch('/api/get_pending_requests', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ student_id: studentId })
        })
        .then(r => r.json())
        .then(result => {
            const tbody = document.querySelector('#pendingcoursestable tbody');
            const emptyRow = document.getElementById('pendingemptyrow');
            if (!tbody) return;

            // حذف الصفوف القديمة مع الإبقاء على صف الفراغ
            tbody.querySelectorAll('tr:not(#pendingemptyrow)').forEach(r => r.remove());

            if (!result.success || result.requests.length === 0) {
                if (emptyRow) emptyRow.style.display = '';
                return;
            }

            if (emptyRow) emptyRow.style.display = 'none';

            result.requests.forEach(req => {
                const tr = document.createElement('tr');
                tr.dataset.requestId = req.request_id;
                tr.innerHTML = `
                    <td>${req.course_id}</td>
                    <td>${req.course_name}</td>
                    <td>${req.credit_hours}</td>
                    <td>${req.section_number}</td>
                    <td>${req.time}</td>
                    <td>${req.days}</td>
                    <td>${req.room}</td>
                    <td>${(parseFloat(req.priority_score) * 100).toFixed(1)}%</td>
                    <td>
                        <button class="btn-delete-req" data-id="${req.request_id}" data-name="${req.course_name}">🗑️</button>
                    </td>
                `;
                tbody.appendChild(tr);
            });

            // ربط أزرار الحذف بالـ modal
            tbody.querySelectorAll('.btn-delete-req').forEach(btn => {
                btn.addEventListener('click', () => openDeleteModal(btn.dataset.id, btn.dataset.name));
            });
        })
        .catch(err => console.error("خطأ أثناء جلب طلبات الانتظار:", err));
    }

    // ── جلب وعرض المواد المسجلة والمثبتة ────────────────────────────────
    function loadRegisteredEnrollments(studentId) {
        fetch('/api/get_registered_enrollments', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ student_id: studentId })
        })
        .then(r => r.json())
        .then(result => {
            const tbody = document.querySelector('#registeredcoursestable tbody');
            const emptyRow = document.getElementById('registeredemptyrow');
            if (!tbody) return;

            tbody.querySelectorAll('tr:not(#registeredemptyrow)').forEach(r => r.remove());

            if (!result.success || result.enrollments.length === 0) {
                if (emptyRow) emptyRow.style.display = '';
                return;
            }

            if (emptyRow) emptyRow.style.display = 'none';

            result.enrollments.forEach(en => {
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td>${en.course_id}</td>
                    <td>${en.course_name}</td>
                    <td>${en.credit_hours}</td>
                    <td>${en.section_number}</td>
                    <td>${en.days} — ${en.time}</td>
                    <td>${en.room}</td>
                    <td><span class="badge-status">${en.status}</span></td>
                `;
                tbody.appendChild(tr);
            });
        })
        .catch(err => console.error("خطأ أثناء جلب المواد المسجلة:", err));
    }

    // تشغيل دوال جلب البيانات الحية من قاعدة البيانات فور تحميل الصفحة
    loadPendingRequests(currentStudentId);
    loadRegisteredEnrollments(currentStudentId);

    // ── دالة إرسال طلب الإضافة (مع دعم تجاوز فحص التخصص) ──────────────
    const msgElement = document.getElementById("reg-msg");

    function resetMsg() {
        msgElement.className = "form-msg";
        msgElement.style.display = "none";
        msgElement.innerHTML = "";
    }

    function sendAddRequest(courseId, sectionNum, forceSpecialization = false) {
        fetch('/api/add_registration_request', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                student_id:           currentStudentId,
                course_id:            courseId,
                section_number:       sectionNum,
                force_specialization: forceSpecialization
            })
        })
        .then(r => r.json())
        .then(result => {
            resetMsg();

            if (result.success) {
                const scoreDisplay = (result.priority_score * 100).toFixed(1);
                msgElement.innerHTML = `
                    ${result.message}<br>
                    <span style="font-size:12px; opacity:0.85;">
                        🎯 الأولوية: <strong>${scoreDisplay}%</strong> — ${result.priority_label}
                    </span>
                `;
                msgElement.classList.add("success");
                document.getElementById("courseid").value = "";
                document.getElementById("sectionnumber").value = "";
                loadPendingRequests(currentStudentId);

            } else if (result.type === "spec_warning") {
                msgElement.classList.add("warning");
                msgElement.innerHTML = `
                    <strong>⚠️ تنبيه — المادة خارج تخصصك</strong><br>
                    هذه المادة غير مدرجة ضمن خطة تخصصك الدراسية.
                    <div class="warning-spec-row">
                        <span class="warning-spec-chip">📚 تخصص المادة: ${result.course_specialization}</span>
                        <span class="warning-spec-chip">🎓 تخصصك: ${result.student_specialization}</span>
                    </div>
                    <div class="warning-actions">
                        <button class="btn-warning-proceed" id="btn-force-reg">✔ متابعة على أي حال</button>
                        <button class="btn-warning-cancel"  id="btn-cancel-reg">✖ إلغاء</button>
                    </div>
                `;
                document.getElementById("btn-force-reg").addEventListener("click", () => {
                    resetMsg();
                    sendAddRequest(courseId, sectionNum, true);
                });
                document.getElementById("btn-cancel-reg").addEventListener("click", resetMsg);

            } else {
                msgElement.innerText = result.message;
                msgElement.classList.add("error");
            }
        })
        .catch(err => {
            console.error("خطأ أثناء إضافة المادة:", err);
            resetMsg();
            msgElement.innerText = "حدث خطأ في الاتصال بالسيرفر، يرجى المحاولة لاحقاً";
            msgElement.classList.add("error");
        });
    }

    // ── ربط حدث زر إضافة المادة ──────────────────────────────────────────
    document.getElementById("btnaddcourse").addEventListener("click", () => {
        const courseIdInput   = document.getElementById("courseid").value.trim();
        const sectionNumInput = document.getElementById("sectionnumber").value.trim();

        resetMsg();

        if (!courseIdInput || !sectionNumInput) {
            msgElement.innerText = "يرجى إدخال رقم المادة ورقم الشعبة أولاً";
            msgElement.classList.add("error");
            return;
        }

        sendAddRequest(courseIdInput, sectionNumInput);
    });

    // ── منطق الـ modal للحذف ──────────────────────────────────────────────
    const deleteModal   = document.getElementById('delete-modal');
    const confirmBtn    = document.getElementById('modal-confirm-btn');
    const cancelBtn     = document.getElementById('modal-cancel-btn');
    const modalCourseName = document.getElementById('modal-course-name');
    let pendingDeleteId = null;

    function openDeleteModal(requestId, courseName) {
        pendingDeleteId = requestId;
        if (modalCourseName) modalCourseName.textContent = `هل أنت متأكد من رغبتك في إزالة "${courseName}" من قائمة الانتظار؟`;
        if (deleteModal) deleteModal.classList.add('active');
    }

    if (cancelBtn) cancelBtn.addEventListener('click', () => {
        deleteModal.classList.remove('active');
        pendingDeleteId = null;
    });

    if (deleteModal) deleteModal.addEventListener('click', (e) => {
        if (e.target === deleteModal) {
            deleteModal.classList.remove('active');
            pendingDeleteId = null;
        }
    });

    if (confirmBtn) confirmBtn.addEventListener('click', () => {
        if (!pendingDeleteId) return;

        fetch('/api/delete_pending_request', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ student_id: currentStudentId, request_id: pendingDeleteId })
        })
        .then(r => r.json())
        .then(result => {
            deleteModal.classList.remove('active');
            pendingDeleteId = null;
            if (result.success) loadPendingRequests(currentStudentId);
            else alert(result.message);
        })
        .catch(err => {
            console.error("خطأ أثناء حذف الطلب:", err);
            deleteModal.classList.remove('active');
        });
    });

    // ── زر تثبيت وإرسال الجدول النهائي ──────────────────────────────────
    const submitBtn = document.getElementById('btnconfirmsubmit');
    if (submitBtn) submitBtn.addEventListener('click', () => {
        alert("📋 سيتم إرسال جدولك عند فتح التسجيل الرسمي تلقائياً.");
    });
});