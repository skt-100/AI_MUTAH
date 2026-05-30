document.addEventListener("DOMContentLoaded", () => {
    const facultiesGrid = document.getElementById('facultiesGrid');
    const searchInput = document.getElementById('searchInput');
    const countEl = document.getElementById('searchCount');
    const noResults = document.getElementById('noResults');

    // دالة استدعاء وبناء الكليات ديناميكياً من السيرفر
    fetch('http://127.0.0.1:5000/api/faculties')
        .then(response => {
            if (!response.ok) throw new Error("فشل الاتصال بقاعدة البيانات");
            return response.json();
        })
        .then(result => {
            if (result.success && result.faculties) {
                renderFaculties(result.faculties);
            }
        })
        .catch(error => {
            console.error("خطأ أثناء تحميل الكليات:", error);
            if (countEl) countEl.textContent = "خطأ في التحميل";
        });

    function renderFaculties(faculties) {
        facultiesGrid.innerHTML = '';
        facultiesGrid.appendChild(noResults);

        faculties.forEach((faculty, index) => {
            const card = document.createElement('a');
            card.className = `faculty-card ${faculty.is_featured ? 'featured' : ''}`;
            
            // التوجيه إلى الصفحة الأساسية المعتمدة بالسيرفر/
            card.href = "main_login.html";
            card.dataset.name = faculty.faculty_name;
            card.style.animationDelay = (index * 0.05) + 's';

            // تفعيل حدث تخزين اسم الكلية عند الضغط
            card.addEventListener('click', () => {
                localStorage.setItem("selectedFaculty", faculty.faculty_name);
            });

            card.innerHTML = `
                <div class="card-top">
                    <div class="faculty-icon">
                        <img src="${faculty.icon_path}" alt="${faculty.faculty_name}" style="width:32px; height:32px; object-fit:contain;">
                    </div>
                    <div class="card-arrow">←</div>
                </div>
                <div>
                    <p class="faculty-name">${faculty.faculty_name}</p>
                    <p class="faculty-desc">${faculty.description}</p>
                </div>
                <div class="card-footer">
                    <span class="year-badge">${faculty.dept_label}</span>
                    <span class="card-action">دخول البوابة ←</span>
                </div>
            `;
            
            facultiesGrid.insertBefore(card, noResults);
        });

        if (countEl) countEl.textContent = faculties.length + ' كلية';
        initLiveSearch();
    }

    function initLiveSearch() {
        if (!searchInput) return;
        searchInput.addEventListener('input', () => {
            const query = searchInput.value.trim().toLowerCase();
            const cards = facultiesGrid.querySelectorAll('.faculty-card');
            let visibleCount = 0;

            cards.forEach(card => {
                const nameAttr = card.dataset.name.toLowerCase();
                const isMatch = !query || nameAttr.includes(query);
                card.style.display = isMatch ? '' : 'none';
                if (isMatch) visibleCount++;
            });

            if (countEl) countEl.textContent = visibleCount + ' كلية';
            if (noResults) noResults.style.display = visibleCount === 0 ? 'block' : 'none';
        });
    }
});
