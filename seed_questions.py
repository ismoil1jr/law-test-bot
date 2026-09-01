from database import SessionLocal, Question

def add_questions():
    db = SessionLocal()
    
    savollar = [
        {
            "text": "O'zbekiston Respublikasining Konstitutsiyasi qachon qabul qilingan?",
            "option_a": "1991-yil 8-dekabr",
            "option_b": "1992-yil 8-dekabr",
            "option_c": "1993-yil 8-dekabr",
            "option_d": "1994-yil 8-dekabr",
            "correct_answer": "B"
        },
        {
            "text": "O'zbekiston Respublikasining davlat tili qaysi?",
            "option_a": "Rus tili",
            "option_b": "O'zbek tili",
            "option_c": "Ingliz tili",
            "option_d": "Qoraqalpoq tili",
            "correct_answer": "B"
        },
        {
            "text": "O'zbekiston Respublikasining prezidenti qancha muddatga saylanadi?",
            "option_a": "4 yil",
            "option_b": "5 yil",
            "option_c": "6 yil",
            "option_d": "7 yil",
            "correct_answer": "B"
        },
        {
            "text": "O'zbekiston Respublikasining qaysi qonuni eng yuqori yuridik kuchga ega?",
            "option_a": "Konstitutsiya",
            "option_b": "Fuqarolik kodeksi",
            "option_c": "Jinoyat kodeksi",
            "option_d": "Mehnat kodeksi",
            "correct_answer": "A"
        },
        {
            "text": "O'zbekiston Respublikasining davlat gerbida qanday tasvirlar bor?",
            "option_a": "Quyosh va paxta",
            "option_b": "Quyosh va bug'doy",
            "option_c": "Quyosh va gul",
            "option_d": "Quyosh va daraxt",
            "correct_answer": "B"
        },
        {
            "text": "O'zbekiston Respublikasining davlat bayrog'i qanday ranglardan iborat?",
            "option_a": "Qizil, oq, yashil",
            "option_b": "Ko'k, oq, yashil",
            "option_c": "Ko'k, qizil, yashil",
            "option_d": "Sariq, oq, yashil",
            "correct_answer": "B"
        },
        {
            "text": "O'zbekiston Respublikasida qaysi tashkilot qonun chiqaruvchi hokimiyatni amalga oshiradi?",
            "option_a": "Prezident",
            "option_b": "Hukumat",
            "option_c": "Oliy Majlis",
            "option_d": "Sudlar",
            "correct_answer": "C"
        },
        {
            "text": "O'zbekiston Respublikasining Konstitutsiyasi nechta bo'limdan iborat?",
            "option_a": "5 bo'lim",
            "option_b": "6 bo'lim",
            "option_c": "7 bo'lim",
            "option_d": "8 bo'lim",
            "correct_answer": "B"
        },
        {
            "text": "O'zbekiston Respublikasining pul birligi nima?",
            "option_a": "Dollar",
            "option_b": "Evro",
            "option_c": "So'm",
            "option_d": "Rubl",
            "correct_answer": "C"
        },
        {
            "text": "O'zbekiston Respublikasi qaysi yilda BMTga a'zo bo'lgan?",
            "option_a": "1991-yil",
            "option_b": "1992-yil",
            "option_c": "1993-yil",
            "option_d": "1994-yil",
            "correct_answer": "B"
        },
        {
            "text": "O'zbekiston Respublikasining birinchi prezidenti kim?",
            "option_a": "Islom Karimov",
            "option_b": "Shavkat Mirziyoyev",
            "option_c": "Nursulton Nazarboyev",
            "option_d": "Emomali Rahmon",
            "correct_answer": "A"
        },
        {
            "text": "O'zbekiston Respublikasining poytaxti qaysi shahar?",
            "option_a": "Samarqand",
            "option_b": "Buxoro",
            "option_c": "Toshkent",
            "option_d": "Andijon",
            "correct_answer": "C"
        },
        {
            "text": "O'zbekiston Respublikasining davlat madhiyasi muallifi kim?",
            "option_a": "Abdulla Oripov",
            "option_b": "Erkin Vohidov",
            "option_c": "Muhammad Yusuf",
            "option_d": "Zulfiya",
            "correct_answer": "A"
        },
        {
            "text": "O'zbekiston Respublikasining Konstitutsiyaviy tuzumi qanday?",
            "option_a": "Prezidentlik",
            "option_b": "Parlamentlik",
            "option_c": "Aralash",
            "option_d": "Monarxiya",
            "correct_answer": "A"
        },
        {
            "text": "O'zbekiston Respublikasida fuqarolar necha yoshdan boshlab ovoz berish huquqiga ega?",
            "option_a": "16 yosh",
            "option_b": "18 yosh",
            "option_c": "20 yosh",
            "option_d": "21 yosh",
            "correct_answer": "B"
        },
        {
            "text": "O'zbekiston Respublikasining sud tizimi qaysi suddan iborat?",
            "option_a": "Konstitutsiyaviy sud, Oliy sud",
            "option_b": "Oliy sud, Tuman sudlari",
            "option_c": "Oliy sud, Viloyat sudlari",
            "option_d": "Barcha javoblar to'g'ri",
            "correct_answer": "D"
        },
        {
            "text": "O'zbekiston Respublikasida qaysi huquq eng muhim hisoblanadi?",
            "option_a": "Yashash huquqi",
            "option_b": "Ta'lim olish huquqi",
            "option_c": "Ishlash huquqi",
            "option_d": "Barchasi muhim",
            "correct_answer": "D"
        },
        {
            "text": "O'zbekiston Respublikasining Konstitutsiyasi qanday qabul qilingan?",
            "option_a": "Referendum orqali",
            "option_b": "Parlament orqali",
            "option_c": "Prezident farmoni bilan",
            "option_d": "Xalq qurultoyida",
            "correct_answer": "A"
        },
        {
            "text": "O'zbekiston Respublikasida qanday iqtisodiy tizim mavjud?",
            "option_a": "Bozor iqtisodiyoti",
            "option_b": "Buyruqbozlik iqtisodiyoti",
            "option_c": "Aralash iqtisodiyot",
            "option_d": "An'anaviy iqtisodiyot",
            "correct_answer": "C"
        },
        {
            "text": "O'zbekiston Respublikasining davlat gerbida qaysi yulduz tasvirlangan?",
            "option_a": "8 qirrali yulduz",
            "option_b": "5 qirrali yulduz",
            "option_c": "12 qirrali yulduz",
            "option_d": "6 qirrali yulduz",
            "correct_answer": "A"
        },
        {
            "text": "O'zbekiston Respublikasining qaysi qonuni huquq va erkinliklarni himoya qiladi?",
            "option_a": "Konstitutsiya",
            "option_b": "Fuqarolik kodeksi",
            "option_c": "Mehnat kodeksi",
            "option_d": "Barchasi",
            "correct_answer": "D"
        },
        {
            "text": "O'zbekiston Respublikasida qanday ta'til kuni davlat mustaqilligi kuni sifatida nishonlanadi?",
            "option_a": "1-sentyabr",
            "option_b": "31-avgust",
            "option_c": "8-dekabr",
            "option_d": "1-may",
            "correct_answer": "A"
        },
        {
            "text": "O'zbekiston Respublikasi qaysi xalqaro tashkilotga a'zo emas?",
            "option_a": "BMT",
            "option_b": "ShHT",
            "option_c": "YevroItifoq",
            "option_d": "MDH",
            "correct_answer": "C"
        },
        {
            "text": "O'zbekiston Respublikasining ichki ishlar organlari qanday nomlanadi?",
            "option_a": "Prokuratura",
            "option_b": "Ichki ishlar vazirligi",
            "option_c": "Milliy gvardiya",
            "option_d": "Barchasi",
            "correct_answer": "D"
        },
        {
            "text": "O'zbekiston Respublikasida qanday soliq tizimi mavjud?",
            "option_a": "Progressiv soliq",
            "option_b": "Regressiv soliq",
            "option_c": "Yagona soliq",
            "option_d": "Barchasi",
            "correct_answer": "C"
        },
        {
            "text": "O'zbekiston Respublikasining davlat ramzlari qaysilar?",
            "option_a": "Bayroq, gerb, madhiya",
            "option_b": "Bayroq, gerb, pasport",
            "option_c": "Gerb, madhiya, pul",
            "option_d": "Bayroq, pul, madhiya",
            "correct_answer": "A"
        },
        {
            "text": "O'zbekiston Respublikasining hududi qancha?",
            "option_a": "447 400 km²",
            "option_b": "400 000 km²",
            "option_c": "500 000 km²",
            "option_d": "300 000 km²",
            "correct_answer": "A"
        },
        {
            "text": "O'zbekiston Respublikasining eng yirik shahri qaysi?",
            "option_a": "Toshkent",
            "option_b": "Samarqand",
            "option_c": "Buxoro",
            "option_d": "Namangan",
            "correct_answer": "A"
        },
        {
            "text": "O'zbekiston Respublikasida qanday dinga e'tiqod qilinadi?",
            "option_a": "Islom",
            "option_b": "Xristianlik",
            "option_c": "Buddizm",
            "option_d": "Barchasi",
            "correct_answer": "D"
        },
        {
            "text": "O'zbekiston Respublikasining eng muhim qonuni nima?",
            "option_a": "Konstitutsiya",
            "option_b": "Jinoyat kodeksi",
            "option_c": "Fuqarolik kodeksi",
            "option_d": "Mehnat kodeksi",
            "correct_answer": "A"
        }
    ]
    
    for s in savollar:
        q = Question(**s)
        db.add(q)
    db.commit()
    db.close()
    print(f"✅ {len(savollar)} ta savol bazaga qo'shildi!")

if __name__ == "__main__":
    add_questions()