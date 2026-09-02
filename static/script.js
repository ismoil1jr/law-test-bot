let userId = null;
let photoUrl = '';
let tgUser = null;

if (window.Telegram && window.Telegram.WebApp) {
    const webApp = window.Telegram.WebApp;
    webApp.ready();
    if (webApp.initDataUnsafe && webApp.initDataUnsafe.user) {
        tgUser = webApp.initDataUnsafe.user;
        userId = tgUser.id;
        if (tgUser.photo_url) photoUrl = tgUser.photo_url;
    }
}

if (!userId) {
    const urlParams = new URLSearchParams(window.location.search);
    const urlUserId = urlParams.get('user_id');
    if (urlUserId) userId = parseInt(urlUserId);
    photoUrl = urlParams.get('photo') || '';
}

if (!userId) {
    alert('❌ Foydalanuvchi ID topilmadi!');
    throw new Error('No user_id found');
}

let questions = [];
let currentIndex = 0;
let answers = {};
let timerInterval = null;
let timeLeft = 900;
let isTestRunning = false;

const pages = {
    home: document.getElementById('home'),
    test: document.getElementById('test'),
    results: document.getElementById('results'),
    profile: document.getElementById('profile')
};
const menuItems = document.querySelectorAll('.menu-item');

function navigateTo(page) {
    Object.keys(pages).forEach(p => {
        pages[p].style.display = (p === page) ? 'block' : 'none';
    });
    menuItems.forEach(item => {
        item.classList.toggle('active', item.dataset.page === page);
    });
    if (page === 'home') loadHome();
    else if (page === 'results') loadResults();
    else if (page === 'profile') loadProfile();
}

menuItems.forEach(item => {
    item.addEventListener('click', () => {
        const page = item.dataset.page;
        if (page === 'test' && !isTestRunning) {
            alert('📝 Test boshlanmagan. Bosh sahifadan "Testni boshlash" tugmasini bosing.');
            return;
        }
        navigateTo(page);
    });
});

async function loadHome() {
    try {
        const res = await fetch(`/api/user/profile?user_id=${userId}`);
        if (res.ok) {
            const data = await res.json();
            document.getElementById('homeTests').textContent = data.tests_remaining || 0;
            document.getElementById('homeTotal').textContent = data.total_tests_taken || 0;
            if (data.tests_remaining > 0) {
                document.getElementById('startTestBtn').style.display = 'flex';
                document.getElementById('noTestsMsg').style.display = 'none';
            } else {
                document.getElementById('startTestBtn').style.display = 'none';
                document.getElementById('noTestsMsg').style.display = 'block';
            }
        }
    } catch (e) {
        console.error(e);
    }
}

document.getElementById('startTestBtn').addEventListener('click', startTest);

async function startTest() {
    try {
        const res = await fetch(`/api/init?user_id=${userId}`);
        const data = await res.json();
        
        if (!res.ok) {
            alert('❌ ' + (data.error || 'Xatolik yuz berdi'));
            return;
        }
        
        questions = data.questions;
        document.getElementById('blockTitleDisplay').textContent = data.block_title || '';
        answers = {};
        questions.forEach(q => answers[q.id] = null);
        currentIndex = 0;
        isTestRunning = true;
        timeLeft = 900;
        
        document.getElementById('timer').style.display = 'flex';
        document.getElementById('finishBtn').style.display = 'flex';
        navigateTo('test');
        renderQuestion();
        startTimer();
    } catch (e) {
        alert('❌ Server bilan bog‘lanishda xatolik!');
    }
}

function renderQuestion() {
    const q = questions[currentIndex];
    if (!q) return;
    
    document.getElementById('questionText').textContent = `${currentIndex + 1}. ${q.text}`;
    const optionsContainer = document.getElementById('optionsContainer');
    const openAnswerContainer = document.getElementById('openAnswerContainer');
    const openInput = document.getElementById('openAnswerInput');

    if (q.q_type === 'open') {
        optionsContainer.style.display = 'none';
        openAnswerContainer.style.display = 'block';
        openInput.value = answers[q.id] || '';

        openInput.oninput = (e) => {
            const val = e.target.value;
            answers[q.id] = val;
            saveAnswer(q.id, val);
            updateCounters();
        };
    } else {
        openAnswerContainer.style.display = 'none';
        optionsContainer.style.display = 'block';

        const letters = ['A', 'B', 'C', 'D'];
        let html = '';
        q.options.forEach((opt, idx) => {
            const letter = letters[idx];
            const selected = (answers[q.id] === letter) ? 'selected' : '';
            html += `<div class="option-item ${selected}" data-id="${q.id}" data-option="${letter}">
                <span class="letter">${letter})</span> ${opt}
            </div>`;
        });
        optionsContainer.innerHTML = html;

        document.querySelectorAll('.option-item').forEach(el => {
            el.onclick = (e) => {
                const qId = parseInt(el.dataset.id);
                const opt = el.dataset.option;
                document.querySelectorAll('.option-item').forEach(i => i.classList.remove('selected'));
                el.classList.add('selected');
                answers[qId] = opt;
                saveAnswer(qId, opt);
                updateCounters();
            };
        });
    }

    updateCounters();
    document.getElementById('prevBtn').disabled = (currentIndex === 0);
    document.getElementById('nextBtn').innerHTML = (currentIndex === questions.length - 1) ? 
        'Yakunlash <i class="fas fa-flag-checkered"></i>' : 
        'Keyingi <i class="fas fa-chevron-right"></i>';
}

function updateCounters() {
    document.getElementById('questionCounter').innerHTML = `<i class="fas fa-question-circle"></i> Savol ${currentIndex + 1}/${questions.length}`;
    const answered = Object.values(answers).filter(v => v !== null && String(v).trim() !== '').length;
    document.getElementById('answeredCounter').innerHTML = `<i class="fas fa-check-circle"></i> Javob: ${answered}/${questions.length}`;
}

async function saveAnswer(qId, val) {
    try {
        await fetch('/api/save', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ user_id: userId, question_id: qId, selected_option: val })
        });
    } catch (e) { console.error(e); }
}

document.getElementById('prevBtn').onclick = () => { if (currentIndex > 0) { currentIndex--; renderQuestion(); } };
document.getElementById('nextBtn').onclick = () => {
    if (currentIndex === questions.length - 1) showFinishModal();
    else { currentIndex++; renderQuestion(); }
};

function startTimer() {
    if (timerInterval) clearInterval(timerInterval);
    timerInterval = setInterval(() => {
        timeLeft--;
        const mins = Math.floor(timeLeft / 60);
        const secs = timeLeft % 60;
        document.getElementById('timerText').textContent = `${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;
        if (timeLeft <= 0) {
            clearInterval(timerInterval);
            finishTest();
        }
    }, 1000);
}

function showFinishModal() {
    const answered = Object.values(answers).filter(v => v !== null && String(v).trim() !== '').length;
    document.getElementById('modalAnswered').textContent = answered;
    document.getElementById('modalUnanswered').textContent = questions.length - answered;
    document.getElementById('finishModal').style.display = 'flex';
}

document.getElementById('cancelFinish').onclick = () => { document.getElementById('finishModal').style.display = 'none'; };
document.getElementById('confirmFinish').onclick = () => {
    document.getElementById('finishModal').style.display = 'none';
    finishTest();
};
document.getElementById('finishBtn').onclick = showFinishModal;

async function finishTest() {
    if (!isTestRunning) return;
    isTestRunning = false;
    clearInterval(timerInterval);
    document.getElementById('timer').style.display = 'none';
    document.getElementById('finishBtn').style.display = 'none';

    try {
        const res = await fetch('/api/finish', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ user_id: userId })
        });
        const data = await res.json();
        alert(`🏁 Test yakunlandi!\n\n✅ To'g'ri: ${data.correct}\n❌ Noto'g'ri: ${data.wrong}\n📊 Foiz: ${data.percentage}%`);
        navigateTo('home');
        loadHome();
    } catch (e) {
        alert('❌ Natijalarni saqlashda xatolik!');
    }
}

async function loadResults() {
    try {
        const res = await fetch(`/api/user/results?user_id=${userId}`);
        const data = await res.json();
        const container = document.getElementById('resultsList');
        if (!data || data.length === 0) {
            container.innerHTML = '<p style="color:rgba(255,255,255,0.5);"><i class="fas fa-inbox"></i> Hali natija yo\'q.</p>';
            return;
        }
        container.innerHTML = data.map(r => `
            <div class="result-item">
                <span><i class="fas fa-check-circle" style="color:#34c759;"></i> ${r.correct}</span>
                <span><i class="fas fa-times-circle" style="color:#ff4757;"></i> ${r.wrong}</span>
                <span><i class="fas fa-percent"></i> ${r.percentage}%</span>
                <span style="font-size:12px;opacity:0.6;"><i class="fas fa-calendar"></i> ${r.date}</span>
            </div>
        `).join('');
    } catch (e) { console.error(e); }
}

async function loadProfile() {
    let fullName = tgUser ? `${tgUser.first_name || ''} ${tgUser.last_name || ''}`.trim() : "Noma'lum";
    let username = tgUser && tgUser.username ? `@${tgUser.username}` : "-";
    document.getElementById('profileName').textContent = fullName;
    document.getElementById('profileUsername').textContent = username;

    const avatarContainer = document.querySelector('.profile-avatar');
    if (photoUrl) {
        avatarContainer.innerHTML = `<img src="${photoUrl}" alt="Avatar" style="width:100%;height:100%;object-fit:cover;" />`;
    }

    try {
        const res = await fetch(`/api/user/profile?user_id=${userId}`);
        if (res.ok) {
            const data = await res.json();
            if (data.full_name) document.getElementById('profileName').textContent = data.full_name;
            if (data.username) document.getElementById('profileUsername').textContent = `@${data.username.replace('@','')}`;
            document.getElementById('profileRemaining').textContent = data.tests_remaining || 0;
            document.getElementById('profileTotal').textContent = data.total_tests_taken || 0;
            if (data.last_result) {
                document.getElementById('lastCorrect').textContent = data.last_result.correct;
                document.getElementById('lastWrong').textContent = data.last_result.wrong;
                document.getElementById('lastPercent').textContent = data.last_result.percentage;
                document.getElementById('lastDate').textContent = data.last_result.date;
            }
        }
    } catch (e) { console.error(e); }
}

navigateTo('home');