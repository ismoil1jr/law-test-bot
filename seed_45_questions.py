from database import SessionLocal, Block, Question

def seed_database():
    db = SessionLocal()
    
    # 1. Yangi blok yaratamiz (agar blok yo'q bo'lsa)
    new_block = Block(title="Huquqshunoslik bo'yicha testlar (45 ta)")
    db.add(new_block)
    db.commit()
    db.refresh(new_block)
    
    block_id = new_block.id
    print(f"Yangi blok yaratildi. ID: {block_id}")

    questions = [
        # ==========================================
        # 35 TA VARIANTLI TEST (MCQ)
        # ==========================================
        {
            "q_type": "mcq",
            "text": "O‘zbekiston Respublikasining Konstitutsiyasi qachon qabul qilingan?",
            "option_a": "1992-yil 8-dekabr",
            "option_b": "1991-yil 31-avgust",
            "option_c": "1993-yil 8-dekabr",
            "option_d": "1990-yil 20-iyun",
            "correct_answer": "A"
        },
        {
            "q_type": "mcq",
            "text": "O‘zbekiston Respublikasida davlat hokimiyatining birinchi va yagona manbai kim?",
            "option_a": "Oliy Majlis",
            "option_b": "Xalq",
            "option_c": "Prezident",
            "option_d": "Sud",
            "correct_answer": "B"
        },
        {
            "q_type": "mcq",
            "text": "O‘zbekiston Respublikasining poytaxti qaysi shahar?",
            "option_a": "Toshkent",
            "option_b": "Samarqand",
            "option_c": "Buxoro",
            "option_d": "Xiva",
            "correct_answer": "A"
        },
        {
            "q_type": "mcq",
            "text": "Fuqarolik muomala layoqati necha yoshdan to‘liq kuchga kiradi?",
            "option_a": "16 yosh",
            "option_b": "14 yosh",
            "option_c": "18 yosh",
            "option_d": "21 yosh",
            "correct_answer": "C"
        },
        {
            "q_type": "mcq",
            "text": "O‘zbekiston Respublikasida qonun chiqaruvchi hokimiyat organini ko‘rsating.",
            "option_a": "Vazirlar Mahkamasi",
            "option_b": "Oliy Majlis",
            "option_c": "Oliy Sud",
            "option_d": "Prokuratura",
            "correct_answer": "B"
        },
        {
            "q_type": "mcq",
            "text": "O‘zbekiston Respublikasi Prezidenti necha yil muddatga saylanadi?",
            "option_a": "7 yil",
            "option_b": "5 yil",
            "option_c": "4 yil",
            "option_d": "6 yil",
            "correct_answer": "A"
        },
        {
            "q_type": "mcq",
            "text": "Inson huquqlari umumjahon deklaratsiyasi BMT tomonidan qaysi yili qabul qilingan?",
            "option_a": "1945-yil",
            "option_b": "1950-yil",
            "option_c": "1948-yil",
            "option_d": "1991-yil",
            "correct_answer": "C"
        },
        {
            "q_type": "mcq",
            "text": "Mehnat kodeksiga ko‘ra normal ish vaqtining davomiyligi haftasiga ko‘pi bilan necha soatdan oshmasligi kerak?",
            "option_a": "40 soat",
            "option_b": "36 soat",
            "option_c": "48 soat",
            "option_d": "30 soat",
            "correct_answer": "A"
        },
        {
            "q_type": "mcq",
            "text": "Mehnat shartnomasi umumiy qoidaga ko‘ra necha yoshdan boshlab tuzilishi mumkin?",
            "option_a": "18 yosh",
            "option_b": "16 yosh",
            "option_c": "15 yosh",
            "option_d": "14 yosh",
            "correct_answer": "B"
        },
        {
            "q_type": "mcq",
            "text": "Sud hokimiyati qaysi hokimiyat tarmog‘iga kiradi?",
            "option_a": "Ijro etuvchi",
            "option_b": "Qonun chiqaruvchi",
            "option_c": "Nazorat qiluvchi",
            "option_d": "Mustaqil sud hokimiyati",
            "correct_answer": "D"
        },
        {
            "q_type": "mcq",
            "text": "Jinoyat kodeksiga ko‘ra umumiy tartibda jinoiy javobgarlik necha yoshdan boshlanadi?",
            "option_a": "16 yosh",
            "option_b": "14 yosh",
            "option_c": "18 yosh",
            "option_d": "13 yosh",
            "correct_answer": "A"
        },
        {
            "q_type": "mcq",
            "text": "O‘zbekiston Respublikasining davlat ramzlariga quyidagilarning qaysi biri kiradi?",
            "option_a": "Davlat gerbi",
            "option_b": "Davlat bayrog'i",
            "option_c": "Davlat madhiyasi",
            "option_d": "Barcha javoblar to'g'ri",
            "correct_answer": "D"
        },
        {
            "q_type": "mcq",
            "text": "Birlashgan Millatlar Tashkilotiga (BMT) O‘zbekiston qachon a’zo bo‘lgan?",
            "option_a": "1991-yil 1-sentabr",
            "option_b": "1992-yil 2-mart",
            "option_c": "1992-yil 8-dekabr",
            "option_d": "1993-yil 10-yanvar",
            "correct_answer": "B"
        },
        {
            "q_type": "mcq",
            "text": "Oila kodeksiga ko‘ra nikoh yoshi erkaklar va ayollar uchun necha yosh etib belgilangan?",
            "option_a": "18 yosh",
            "option_b": "17 yosh",
            "option_c": "20 yosh",
            "option_d": "16 yosh",
            "correct_answer": "A"
        },
        {
            "q_type": "mcq",
            "text": "Mulkdor o‘z mulkiga nisbatan qanday huquqlarga ega?",
            "option_a": "Faqat egalik qilish",
            "option_b": "Faqat foydalanish",
            "option_c": "Faqat tasarruf etish",
            "option_d": "Egalik qilish, foydalanish va tasarruf etish",
            "correct_answer": "D"
        },
        {
            "q_type": "mcq",
            "text": "Ma’muriy javobgarlik to‘g‘risidagi kodeksga ko‘ra ma’muriy qamoq muddati ko‘pi bilan necha sutka?",
            "option_a": "10 sutka",
            "option_b": "30 sutka",
            "option_c": "15 sutka",
            "option_d": "60 sutka",
            "correct_answer": "C"
        },
        {
            "q_type": "mcq",
            "text": "O‘zbekiston Respublikasida sud qarorlari kim nomidan chiqariladi?",
            "option_a": "O‘zbekiston Respublikasi nomidan",
            "option_b": "Sudya nomidan",
            "option_c": "Oliy Sud nomidan",
            "option_d": "Adliya vazirligi nomidan",
            "correct_answer": "A"
        },
        {
            "q_type": "mcq",
            "text": "Oliy Majlis Qonunchilik palatasi spikerini kim saylaydi?",
            "option_a": "Prezident",
            "option_b": "Qonunchilik palatasi deputatlari",
            "option_c": "Senat a'zolari",
            "option_d": "Xalq",
            "correct_answer": "B"
        },
        {
            "q_type": "mcq",
            "text": "Prokuratura organlari tizimiga kim boshchilik qiladi?",
            "option_a": "O‘zbekiston Respublikasi Bosh prokurori",
            "option_b": "Adliya vaziri",
            "option_c": "Oliy Sud raisi",
            "option_d": "Ichki ishlar vaziri",
            "correct_answer": "A"
        },
        {
            "q_type": "mcq",
            "text": "O‘zbekiston Respublikasining pul birligi nima?",
            "option_a": "Dollar",
            "option_b": "Yevro",
            "option_c": "So‘m",
            "option_d": "Ruble",
            "correct_answer": "C"
        },
        {
            "q_type": "mcq",
            "text": "Xodimga har yilgi asosiy mehnat ta’tili kamida necha ish kuni beriladi?",
            "option_a": "15 ish kuni",
            "option_b": "21 ish kuni",
            "option_c": "30 ish kuni",
            "option_d": "24 ish kuni",
            "correct_answer": "B"
        },
        {
            "q_type": "mcq",
            "text": "Qaysi xalqaro hujjat inson huquqlarining asosiy manbai hisoblanadi?",
            "option_a": "Inson huquqlari umumjahon deklaratsiyasi",
            "option_b": "Parij konvensiyasi",
            "option_c": "Vena shartnomasi",
            "option_d": "Rim statuti",
            "correct_answer": "A"
        },
        {
            "q_type": "mcq",
            "text": "Huquq va majburiyatlarga ega bo‘lish qobiliyati nima deyiladi?",
            "option_a": "Muomala layoqati",
            "option_b": "Huquq layoqati",
            "option_c": "Javobgarlik layoqati",
            "option_d": "Muomala layoqatsizligi",
            "correct_answer": "B"
        },
        {
            "q_type": "mcq",
            "text": "O‘zbekiston Respublikasi Konstitutsiyasining yangi tahriri qachon umumxalq referendumi orqali qabul qilingan?",
            "option_a": "2022-yil 8-dekabr",
            "option_b": "2023-yil 1-yanvar",
            "option_c": "2023-yil 30-aprel",
            "option_d": "2023-yil 31-avgust",
            "correct_answer": "C"
        },
        {
            "q_type": "mcq",
            "text": "Voyaga yetmagan bolalariga ta’minot berish (aliment) majburiyati kimning zimmasida?",
            "option_a": "Ota-ona",
            "option_b": "Davlat",
            "option_c": "Maktab",
            "option_d": "Vasiflik organi",
            "correct_answer": "A"
        },
        {
            "q_type": "mcq",
            "text": "O‘zbekiston Respublikasining Oliy sudi sudyalarini kim saylaydi?",
            "option_a": "Prezident",
            "option_b": "Oliy Majlis Senati",
            "option_c": "Qonunchilik palatasi",
            "option_d": "Adliya vazirligi",
            "correct_answer": "B"
        },
        {
            "q_type": "mcq",
            "text": "Davlat hokimiyatining bo‘linishi prinsipiga ko‘ra hokimiyat necha tarmoqqa bo‘linadi?",
            "option_a": "2",
            "option_b": "4",
            "option_c": "3",
            "option_d": "5",
            "correct_answer": "C"
        },
        {
            "q_type": "mcq",
            "text": "Yuridik shaxs maqomi qachondan e’tiboran vujudga keladi?",
            "option_a": "Davlat ro‘yxatidan o‘tkazilgan paytdan",
            "option_b": "Ustav tasdiqlangan paytdan",
            "option_c": "Shartnoma tuzilgan paytdan",
            "option_d": "Hissadorlar yig‘ilgan paytdan",
            "correct_answer": "A"
        },
        {
            "q_type": "mcq",
            "text": "Jinoyat tarkibining nechta elementi bor?",
            "option_a": "2 ta",
            "option_b": "4 ta",
            "option_c": "3 ta",
            "option_d": "5 ta",
            "correct_answer": "B"
        },
        {
            "q_type": "mcq",
            "text": "Mehnat shartnomasini bekor qilish haqida xodim ish beruvchini kamida necha kun oldin ogohlantirishi kerak?",
            "option_a": "7 kun",
            "option_b": "10 kun",
            "option_c": "14 kun",
            "option_d": "30 kun",
            "correct_answer": "C"
        },
        {
            "q_type": "mcq",
            "text": "Fuqaroning muomala layoqatini cheklash faqat kim tomonidan amalga oshiriladi?",
            "option_a": "Sud",
            "option_b": "Prokuratura",
            "option_c": "IIB",
            "option_d": "Hokimiyat",
            "correct_answer": "A"
        },
        {
            "q_type": "mcq",
            "text": "Muayyan huquqbuzarlik uchun javobgarlikni belgilovchi huquqiy norma qismi nima deyiladi?",
            "option_a": "Gipoteza",
            "option_b": "Dispozitsiya",
            "option_c": "Preambula",
            "option_d": "Sanksiya",
            "correct_answer": "D"
        },
        {
            "q_type": "mcq",
            "text": "Saylov huquqiga ega bo‘lgan fuqarolar necha yoshdan saylovda qatnashadi?",
            "option_a": "16 yosh",
            "option_b": "18 yosh",
            "option_c": "21 yosh",
            "option_d": "25 yosh",
            "correct_answer": "B"
        },
        {
            "q_type": "mcq",
            "text": "Mahkamaning aybsizlik prezumpsiyasi qaysi hujjatda kafolatlangan?",
            "option_a": "Konstitutsiya",
            "option_b": "Nizom",
            "option_c": "Buyruq",
            "option_d": "Ko'rsatma",
            "correct_answer": "A"
        },
        {
            "q_type": "mcq",
            "text": "O‘zbekiston Respublikasining Oliy Majlisi necha palatadan iborat?",
            "option_a": "1 palata",
            "option_b": "2 palata",
            "option_c": "3 palata",
            "option_d": "Palatasiz",
            "correct_answer": "B"
        },

        # ==========================================
        # 10 TA OCHIQ TEST (OPEN)
        # ==========================================
        {
            "q_type": "open",
            "text": "O‘zbekiston Respublikasida qonun chiqaruvchi oliy davlat vakillik organi qaysi?",
            "option_a": None, "option_b": None, "option_c": None, "option_d": None,
            "correct_answer": "Oliy Majlis"
        },
        {
            "q_type": "open",
            "text": "O‘zbekiston Respublikasida odil sudlovni faqat qaysi organ amalga oshiradi?",
            "option_a": None, "option_b": None, "option_c": None, "option_d": None,
            "correct_answer": "Sud"
        },
        {
            "q_type": "open",
            "text": "Insonning tug‘ilgandan boshlab daxlsiz bo‘lgan va tortib olinmaydigan asosiy huquqi nima?",
            "option_a": None, "option_b": None, "option_c": None, "option_d": None,
            "correct_answer": "Yashash huquqi"
        },
        {
            "q_type": "open",
            "text": "O‘zbekiston Respublikasining davlat tili qaysi?",
            "option_a": None, "option_b": None, "option_c": None, "option_d": None,
            "correct_answer": "O'zbek tili"
        },
        {
            "q_type": "open",
            "text": "Fuqaro va ish beruvchi o‘rtasidagi mehnat munosabatlarini tartibga soluvchi asosiy kelishuv nima deb ataladi?",
            "option_a": None, "option_b": None, "option_c": None, "option_d": None,
            "correct_answer": "Mehnat shartnomasi"
        },
        {
            "q_type": "open",
            "text": "Shaxsning aybi qonuniy tartibda isbotlanmaguncha u nima hisoblanadi?",
            "option_a": None, "option_b": None, "option_c": None, "option_d": None,
            "correct_answer": "Aybsiz"
        },
        {
            "q_type": "open",
            "text": "O‘zbekiston Respublikasi Bosh vazirini lavozimga kim tayinlaydi?",
            "option_a": None, "option_b": None, "option_c": None, "option_d": None,
            "correct_answer": "Prezident"
        },
        {
            "q_type": "open",
            "text": "Fuqaroning huquq va erkinliklarini himoya qiluvchi eng oliy yuridik kuchga ega davlat hujjati nima?",
            "option_a": None, "option_b": None, "option_c": None, "option_d": None,
            "correct_answer": "Konstitutsiya"
        },
        {
            "q_type": "open",
            "text": "Sudda fuqaroning huquq va qonuniy manfaatlarini himoya qiluvchi professional shaxs kim?",
            "option_a": None, "option_b": None, "option_c": None, "option_d": None,
            "correct_answer": "Advokat"
        },
        {
            "q_type": "open",
            "text": "Qonun loyihalarini qabul qiluvchi Oliy Majlis palatasi qaysi?",
            "option_a": None, "option_b": None, "option_c": None, "option_d": None,
            "correct_answer": "Qonunchilik palatasi"
        }
    ]

    # Savollarni birma-bir bazaga qo'shamiz
    for q in questions:
        question_obj = Question(
            block_id=block_id,
            q_type=q["q_type"],
            text=q["text"],
            option_a=q["option_a"],
            option_b=q["option_b"],
            option_c=q["option_c"],
            option_d=q["option_d"],
            correct_answer=q["correct_answer"]
        )
        db.add(question_obj)

    db.commit()
    db.close()
    print("✅ 45 ta test (35 ta MCQ va 10 ta Open) bazaga muvaffaqiyatli qo'shildi!")

if __name__ == "__main__":
    seed_database()