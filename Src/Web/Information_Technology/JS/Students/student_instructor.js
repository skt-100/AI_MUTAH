// student_instructor.js — جلب الهيئة التدريسية وحقن المكونات وعرض الكاروسيل الأفقي مع البحث الفوري
document.addEventListener("DOMContentLoaded", async () => {

    const currentStudentId = localStorage.getItem("userId");

    // 1. التحقق من أمان الجلسة أولاً
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

    // 2. جلب ملفات الواجهة المشتركة (التوب بار والسايدبار) وحقنها برمجياً
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

    // ربط عناصر الكاروسيل بالواجهة
    const track       = document.getElementById("carouselTrack");
    const prevBtn      = document.getElementById("prevBtn");
    const nextBtn      = document.getElementById("nextBtn");
    const dotsWrap     = document.getElementById("carouselDots");
    const searchInput = document.getElementById("searchInstructor");

    const CARD_WIDTH  = 220;   
    const CARD_GAP    = 20;    
    let   currentIdx  = 0;
    let   allCards    = [];    

    const visibleCount = () => {
        const viewportW = document.getElementById("carouselViewport")?.offsetWidth || 700;
        return Math.max(1, Math.floor((viewportW + CARD_GAP) / (CARD_WIDTH + CARD_GAP)));
    };

    const moveTo = (idx) => {
        if (!track) return;
        const cards    = track.querySelectorAll(".instructor-card");
        const maxIdx   = Math.max(0, cards.length - visibleCount());
        currentIdx     = Math.min(Math.max(0, idx), maxIdx);
        const offset   = currentIdx * (CARD_WIDTH + CARD_GAP);
        
        track.style.transform = `translateX(${offset}px)`;

        if (prevBtn) prevBtn.disabled = currentIdx === 0;
        if (nextBtn) nextBtn.disabled = currentIdx >= maxIdx;

        if (dotsWrap) {
            dotsWrap.querySelectorAll(".dot").forEach((d, i) => {
                d.classList.toggle("active", i === currentIdx);
            });
        }
    };

    const buildDots = (count) => {
        if (!dotsWrap) return;
        dotsWrap.innerHTML = "";
        for (let i = 0; i < count; i++) {
            const dot = document.createElement("button");
            dot.className = "dot" + (i === 0 ? " active" : "");
            dot.addEventListener("click", () => moveTo(i));
            dotsWrap.appendChild(dot);
        }
    };

    if (prevBtn) prevBtn.addEventListener("click", () => moveTo(currentIdx - 1));
    if (nextBtn) nextBtn.addEventListener("click", () => moveTo(currentIdx + 1));

    // 3. جلب بيانات الهيئة التدريسية المحدثة المصححة
    fetch('/api/student_instructor')
        .then(res => {
            if (!res.ok) throw new Error("فشل الاتصال بالسيرفر");
            return res.json();
        })
        .then(result => {
            if (!track) return;
            track.innerHTML = "";
            allCards = [];

            if (!result.success || result.data.length === 0) {
                track.innerHTML = `<div class="carousel-loading">⚠️ لا يوجد مدرسون مضافون حالياً في الكلية.</div>`;
                return;
            }

            result.data.forEach((teacher, i) => {
                const card = document.createElement("div");
                card.className = "instructor-card";
                card.style.animationDelay = (i * 0.06) + "s";

                // وضع رمز تعبيري ذكي بناءً على الرتبة الأكاديمية نظراً لعدم وجود صور في قاعدة البيانات
                let rankEmoji = "👨‍🏫";
                if (teacher.academic_rank && teacher.academic_rank.includes("بروفيسور")) rankEmoji = "🔬";
                else if (teacher.academic_rank && teacher.academic_rank.includes("دكتور")) rankEmoji = "🎓";

                card.innerHTML = `
                    <div class="instructor-avatar" style="display:flex; justify-content:center; align-items:center; font-size:40px; background:#f5dbdb; border-radius:50%; width:80px; height:80px; margin:0 auto 12px;">${rankEmoji}</div>
                    <h3 class="instructor-name">${teacher.full_name}</h3>
                    <span class="instructor-rank">${teacher.academic_rank || "عضو هيئة تدريس"}</span>
                    <p style="font-size:11px; color:#888; margin-top:4px;">${teacher.specialization || "كلية IT"}</p>
                    <div class="instructor-dots">
                        <span></span><span></span><span></span>
                    </div>
                `;

                track.appendChild(card);
                allCards.push(card);
            });

            const maxIdx = Math.max(0, allCards.length - visibleCount());
            buildDots(maxIdx + 1);
            moveTo(0);
        })
        .catch(err => {
            console.error("خطأ أثناء جلب المدرسين:", err);
            if (track) {
                track.innerHTML = `<div class="carousel-loading" style="color:#e74c3c;">❌ حدث خطأ داخلي أثناء تحميل أعضاء الهيئة التدريسية.</div>`;
            }
        });

    window.addEventListener("resize", () => moveTo(currentIdx));

    // 4. منطق الفلترة الفورية بالبحث السريع عن المدرسين
    if (searchInput) {
        searchInput.addEventListener("input", () => {
            const query = searchInput.value.trim().toLowerCase();

            allCards.forEach(card => {
                const name = card.querySelector(".instructor-name")?.textContent.toLowerCase() || "";
                const show = !query || name.includes(query);
                card.style.display = show ? "" : "none";
            });

            moveTo(0);
        });
    }
});
