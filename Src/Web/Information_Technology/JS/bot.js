document.addEventListener("DOMContentLoaded", () => {

    // 1. ربط ملف الـ CSS ديناميكياً عبر المسار المطلق الثابت
    const linkElement = document.createElement("link");
    linkElement.rel   = "stylesheet";
    linkElement.href  = "/Information_Technology/CSS/bot.css";
    document.head.appendChild(linkElement);

    // 2. حقن هيكل الـ Widget داخل الـ Body بالمسارات المطلقة الجديدة للأيقونات
    const chatHTML = `
        <div class="chat-widget-window" id="chatWidgetWindow">
            <div class="chat-widget-header">
                <div class="bot-profile-mini">
                    <div class="bot-avatar-emoji">🤖</div>
                    <div class="bot-info-meta">
                        <h4 class="bot-name-text">المساعد الأكاديمي</h4>
                        <span class="bot-status-indicator">نشط الآن</span>
                    </div>
                </div>
                <button class="chat-close-x" id="chatCloseX">&times;</button>
            </div>
            <div class="chat-widget-body" id="chatWidgetBody">

                <div class="widget-msg bot-row">
                    <div class="widget-bubble">
                        مرحباً بك! 👋 أنا مساعدك الأكاديمي لجامعة مؤتة.<br>
                        يمكنني مساعدتك في المواضيع التالية: <br><br>
                        - التعليمات الجامعية<br>
                        - القوانين الجامعية<br>
                        - جريدة المواد<br>
                        - أعضاء الهيئة التدريسية<br>
                        - الخطط الدراسية<br>
                    </div>
                </div>

            </div>
            <div class="chat-widget-footer">
                <input type="text" id="chatWidgetInput" placeholder="اكتب استفسارك هنا..." dir="rtl">
                <button id="chatWidgetSendBtn">➤</button>
            </div>
        </div>

        <button class="chat-fab" id="chatWidgetToggle" aria-label="المساعد الأكاديمي">
            <img src="/Information_Technology/.img/bot_icon.png" alt="المساعد">
            <span class="fab-dot"></span>
        </button>
    `;

    const container = document.createElement("div");
    container.innerHTML = chatHTML;
    document.body.appendChild(container);

    // 3. ربط العناصر بعد حقنها مباشرة في الـ DOM
    const widgetToggle  = document.getElementById("chatWidgetToggle");
    const widgetWindow  = document.getElementById("chatWidgetWindow");
    const chatCloseX    = document.getElementById("chatCloseX");
    const widgetInput   = document.getElementById("chatWidgetInput");
    const widgetSendBtn = document.getElementById("chatWidgetSendBtn");
    const widgetBody    = document.getElementById("chatWidgetBody");

    // ─── فتح وإغلاق الـ Widget ───
    widgetToggle.addEventListener("click", () => {
        widgetWindow.classList.toggle("open");
        if (widgetWindow.classList.contains("open")) widgetInput.focus();
    });

    chatCloseX.addEventListener("click", () => {
        widgetWindow.classList.remove("open");
    });

    // ─── الضغط على خيارات البطاقات التفاعلية إن وجدت ───
    widgetBody.addEventListener("click", (e) => {
        const btn = e.target.closest(".bot-topic-btn");
        if (btn) {
            const msg = btn.dataset.msg;
            const topics = widgetBody.querySelector(".bot-topics");
            if (topics) topics.remove();
            processSend(msg);
        }
    });

    // ─── دالة معالجة وإرسال الرسائل ───
    function processSend(forcedText = null) {
        const text = forcedText || widgetInput.value.trim();
        if (!text) return;

        // إظهار رسالة المستخدم داخل الواجهة
        appendWidgetMessage(text, true);
        widgetInput.value = "";

        // إظهار مؤشر التحميل أثناء انتظار رد السيرفر
        const loadingId = showLoadingIndicator();

        // إرسال النص إلى الـ API الخاص بالبوت في الـ Flask
        fetch('/api/bot', {
            method:  'POST',
            headers: { 'Content-Type': 'application/json' },
            body:    JSON.stringify({
                student_id: localStorage.getItem('userId'),
                message:    text
            })
        })
        .then(res => {
            if (!res.ok) throw new Error();
            return res.json();
        })
        .then(data => {
            removeLoadingIndicator(loadingId);
            if (data.success) {
                appendWidgetMessage(data.answer, false);
            } else {
                appendWidgetMessage("عذراً، حدث خطأ أثناء المعالجة. حاول مجدداً.", false);
            }
        })
        .catch(() => {
            removeLoadingIndicator(loadingId);
            appendWidgetMessage("تعذّر الاتصال بالسيرفر. تأكد من تشغيل ملف run.py الخاص بالمشروع.", false);
        });
    }

    // ─── إضافة رسالة للمحادثة ───
    function appendWidgetMessage(text, isUser = true) {
        const msgRow      = document.createElement("div");
        msgRow.className  = `widget-msg ${isUser ? 'user-row' : 'bot-row'}`;
        msgRow.innerHTML  = `<div class="widget-bubble">${text}</div>`;
        widgetBody.appendChild(msgRow);
        widgetBody.scrollTop = widgetBody.scrollHeight;
    }

    // ─── مؤشر التحميل (النُقاط الثلاث) ───
    function showLoadingIndicator() {
        const id      = `loading-${Date.now()}`;
        const msgRow  = document.createElement("div");
        msgRow.className = "widget-msg bot-row";
        msgRow.id        = id;
        msgRow.innerHTML = `<div class="widget-bubble">...</div>`;
        widgetBody.appendChild(msgRow);
        widgetBody.scrollTop = widgetBody.scrollHeight;
        return id;
    }

    function removeLoadingIndicator(id) {
        const el = document.getElementById(id);
        if (el) el.remove();
    }

    // ─── تفعيل أحداث الإرسال عند الضغط أو النقر ───
    if (widgetSendBtn) {
        widgetSendBtn.addEventListener("click", () => processSend());
    }
    
    if (widgetInput) {
        widgetInput.addEventListener("keypress", (e) => {
            if (e.key === "Enter") processSend();
        });
    }
});
