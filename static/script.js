// -------------------- Telegram WebApp dan user_id olish --------------------
let userId = null;
let photoUrl = '';

// 1-usul: Telegram WebApp API (asosiy)
if (window.Telegram && window.Telegram.WebApp) {
    const webApp = window.Telegram.WebApp;
    webApp.ready(); // WebApp tayyorligini bildirish
    
    if (webApp.initDataUnsafe && webApp.initDataUnsafe.user) {
        const user = webApp.initDataUnsafe.user;
        userId = user.id;
        // Telegram avatar URL ni bermaydi, lekin zaxira
        if (user.photo_url) {
            photoUrl = user.photo_url;
        }
    }
}

// 2-usul: URL parametrlaridan olish (zaxira, brauzerda sinash uchun)
if (!userId) {
    const urlParams = new URLSearchParams(window.location.search);
    const urlUserId = urlParams.get('user_id');
    if (urlUserId) {
        userId = parseInt(urlUserId);
    }
    photoUrl = urlParams.get('photo') || '';
}

// Agar hali ham userId bo'lmasa, xatolik
if (!userId) {
    alert('❌ Foydalanuvchi ID topilmadi! Iltimos, bot orqali qayta urinib ko‘ring.');
    throw new Error('No user_id found');
}

// -------------------- Qolgan kod --------------------
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

// -------------------- HOME --------------------
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
        console.error('Home yuklashda xatolik:', e);
    }
}

document.getElementById('startTestBtn').addEventListener('click', startTest);

// -------------------- TESTNI BOSHLASH --------------------
async function startTest() {
    try {
        const res = await fetch(`/api/init?user_id=${userId}`);
        const data = await res.json();
        
        if (!res.ok) {
            alert('❌ ' + (data.error || 'Xatolik yuz berdi'));
            return;
        }
        
        if (data.status === 'finished') {
            alert('ℹ️ ' + data.message);
            return;
        }
        
        questions = data.questions;
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
        console.error(e);
    }
}

// -------------------- SAVOLNI KO'RSATISH --------------------
function renderQuestion() {
    const q = questions[currentIndex];
    if (!q) return;
    
    document.getElementById('questionText').textContent = q.text;
    const letters = ['A', 'B', 'C', 'D'];
    let html = '';
    q.options.forEach((opt, idx) => {
        const letter = letters[idx];
        const selected = (answers[q.id] === letter) ? 'selected' : '';
        html += `<div class="option-item ${selected}" data-id="${q.id}" data-option="${letter}">
            <span class="letter">${letter})</span> ${opt}
        </div>`;
    });
    document.getElementById('optionsContainer').innerHTML = html;
    
    document.querySelectorAll('.option-item').forEach(el => {
        el.addEventListener('click', onOptionClick);
    });
    
    document.getElementById('questionCounter').innerHTML = 
        `<i class="fas fa-question-circle"></i> Savol ${currentIndex+1}/${questions.length}`;
    
    const answered = Object.values(answers).filter(v => v !== null).length;
    document.getElementById('answeredCounter').innerHTML = 
        `<i class="fas fa-check-circle"></i> Javob: ${answered}/${questions.length}`;
    
    document.getElementById('prevBtn').disabled = (currentIndex === 0);
    document.getElementById('nextBtn').innerHTML = (currentIndex === questions.length-1) ? 
        'Yakunlash <i class="fas fa-flag-checkered"></i>' : 
        'Keyingi <i class="fas fa-chevron-right"></i>';
}

// -------------------- JAVOB TANLASH --------------------
async function onOptionClick(e) {
    const el = e.currentTarget;
    const qId = parseInt(el.dataset.id);
    const option = el.dataset.option;
    
    document.querySelectorAll('.option-item').forEach(item => item.classList.remove('selected'));
    el.classList.add('selected');
    answers[qId] = option;
    
    try {
        await fetch('/api/save', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                user_id: userId, 
                question_id: qId, 
                selected_option: option 
            })
        });
    } catch (e) {
        console.error('Javob saqlashda xatolik:', e);
    }
    
    const answered = Object.values(answers).filter(v => v !== null).length;
    document.getElementById('answeredCounter').innerHTML = 
        `<i class="fas fa-check-circle"></i> Javob: ${answered}/${questions.length}`;
}

// -------------------- NAVIGATSIYA --------------------
document.getElementById('prevBtn').addEventListener('click', () => {
    if (currentIndex > 0) {
        currentIndex--;
        renderQuestion();
    }
});

document.getElementById('nextBtn').addEventListener('click', () => {
    if (currentIndex === questions.length - 1) {
        showFinishModal();
    } else {
        currentIndex++;
        renderQuestion();
    }
});

// -------------------- TAYMER --------------------
function startTimer() {
    if (timerInterval) clearInterval(timerInterval);
    timerInterval = setInterval(() => {
        timeLeft--;
        const mins = Math.floor(timeLeft / 60);
        const secs = timeLeft % 60;
        document.getElementById('timerText').textContent = 
            `${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;
        
        if (timeLeft <= 0) {
            clearInterval(timerInterval);
            alert('⏰ Vaqt tugadi! Test avtomatik yakunlanmoqda...');
            finishTest();
        }
    }, 1000);
}

// -------------------- TUGATISH MODAL --------------------
function showFinishModal() {
    const answered = Object.values(answers).filter(v => v !== null).length;
    const unanswered = questions.length - answered;
    document.getElementById('modalAnswered').textContent = answered;
    document.getElementById('modalUnanswered').textContent = unanswered;
    document.getElementById('finishModal').style.display = 'flex';
}

document.getElementById('cancelFinish').onclick = () => {
    document.getElementById('finishModal').style.display = 'none';
};

document.getElementById('confirmFinish').onclick = () => {
    document.getElementById('finishModal').style.display = 'none';
    finishTest();
};

document.getElementById('finishBtn').onclick = showFinishModal;

// -------------------- TESTNI TUGATISH --------------------
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
        
        alert(`🏁 Test yakunlandi!\n\n✅ To'g'ri: ${data.correct}\n❌ Noto'g'ri: ${data.wrong}\n📊 Foiz: ${data.percentage}%\n\n📋 Batafsil natijalar "Natijalar" bo'limida.`);
        
        navigateTo('home');
        loadHome();
    } catch (e) {
        alert('❌ Natijalarni saqlashda xatolik!');
        console.error(e);
    }
}

// -------------------- NATIJALAR --------------------
async function loadResults() {
    try {
        const res = await fetch(`/api/user/results?user_id=${userId}`);
        const data = await res.json();
        const container = document.getElementById('resultsList');
        
        if (data.length === 0) {
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
    } catch (e) {
        console.error('Natijalarni yuklashda xatolik:', e);
    }
}

// -------------------- PROFIL --------------------
async function loadProfile() {
    try {
        const res = await fetch(`/api/user/profile?user_id=${userId}`);
        const data = await res.json();
        
        document.getElementById('profileName').textContent = data.full_name || 'Noma\'lum';
        document.getElementById('profileUsername').textContent = data.username || '-';
        document.getElementById('profileRemaining').textContent = data.tests_remaining || 0;
        document.getElementById('profileTotal').textContent = data.total_tests_taken || 0;
        
        // Avatar
        const avatarContainer = document.querySelector('.profile-avatar');
        if (photoUrl) {
            avatarContainer.innerHTML = `<img src="${photoUrl}" alt="Avatar" style="width:100%;height:100%;object-fit:cover;" />`;
        } else {
            avatarContainer.innerHTML = `<i class="fas fa-user-circle" style="font-size:56px; color:rgba(255,255,255,0.3);"></i>`;
        }
        
        // Oxirgi natija
        if (data.last_result) {
            document.getElementById('lastCorrect').textContent = data.last_result.correct;
            document.getElementById('lastWrong').textContent = data.last_result.wrong;
            document.getElementById('lastPercent').textContent = data.last_result.percentage;
            document.getElementById('lastDate').textContent = data.last_result.date;
        } else {
            document.getElementById('lastResultBox').innerHTML = 
                '<p style="color:rgba(255,255,255,0.4);"><i class="fas fa-info-circle"></i> Hali natija yo\'q</p>';
        }
    } catch (e) {
        console.error('Profilni yuklashda xatolik:', e);
    }
}

// -------------------- BOSHLASH --------------------
navigateTo('home');