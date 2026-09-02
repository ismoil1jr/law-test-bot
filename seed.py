import sqlite3

DB_NAME = "database.db"  # Bazangiz fayl nomi (app.db yoki database.db)

questions_data = [
    # ---------------- 35 TA YOPIQ TEST (A, B, C, D) ----------------
    {
        "text": "1. Quyidagilar orasidan Noto`g`ri mulohaza berilgan javobni toping. (Asos: 1-modda)",
        "options": "A) Oʻzbekiston Respublikasining referendumi Oʻzbekiston Respublikasining qonunlarini va boshqa qarorlarni qabul qilish maqsadlarida jamiyat va davlat hayotining eng muhim masalalari yuzasidan fuqarolarning umumxalq ovoz berishidir.\nB) Referendum saylovlar bilan bir qatorda xalq irodasining bevosita ifodasidir.\nC) Agar referendumda qabul qilingan qarorlarda boshqacha tartib nazarda tutilgan boʻlmasa, referendumda qabul qilingan qarorlar faqat referendum yoʻli bilan bekor qilinishi yoki oʻzgartirilishi mumkin.\nD) Referendumda qabul qilingan qarorlar oliy yuridik kuchga ega emas.",
        "correct_answer": "D",
        "block_id": 1
    },
    {
        "text": "2. Quyidagilar orasidan referendum predmeti bo`la olmaydigan masalalar to`g`ri keltirilgan javobni toping. (Asos: 2-modda)\n1) Oʻzbekiston Respublikasining hududiy yaxlitligini oʻzgartirish doir masala\n2) Chet elga ijtimoiy yordam berishga doir masala\n3) amnistiya va afv etishga doir masala\n4) O`zbekiston Respublikasi Konstitutsiyasiga o`zgartirish va qo`shimchalar kiritishga doir masala",
        "options": "A) 1,3\nB) 1,4\nC) 2,3\nD) 2,4",
        "correct_answer": "C",
        "block_id": 1
    },
    {
        "text": "3. Oʻzbekiston Respublikasining butun hududida joriy etilgan harbiy vaqt yoki favqulodda holat sharoitlarida, shuningdek harbiy vaqt tugagan yoki favqulodda holat bekor qilingandan keyin (a)-qancha muddat davomida referendum oʻtkazilmaydi?\nReferendum natijalari rasman eʼlon qilingandan keyin (b)-qancha muddat davomida mazmun yoki maʼnosiga koʻra xuddi shunday savol qoʻyilgan referendum oʻtkazilmaydi? (Asos: 3-modda)",
        "options": "A) a-2, b-3\nB) a-1, b-3\nC) a-2, b-4\nD) a-1, b-4",
        "correct_answer": "D",
        "block_id": 1
    },
    {
        "text": "4. To`g`ri mulohazalar berilgan javobni toping. (Asos: 5-modda)\n1) Referendum fuqarolarning oʻz xohish-irodasini umumiy, teng va toʻgʻridan-toʻgʻri bildirishi asosida yashirin ovoz berish yoʻli bilan oʻtkaziladi.\n2) Oʻzbekiston Respublikasi fuqarolari referendumda teng asoslarda ishtirok etadilar.\n3) Oʻzbekiston Respublikasi fuqarolarining referendumda ishtirok etishi majburiy.\n4) Fuqarolarning oʻz xohish-irodasini bildirishi nazorat qilinishiga yoʻl qoʻyiladi.\n5) Oʻzbekiston Respublikasi fuqarolari referendumda vakillari bilan birga ishtirok etadi.\n6) Oʻzbekiston Respublikasi fuqarolarini referendumda ishtirok etishga yoki ishtirok etmaslikka majbur qilish maqsadida ularga taʼsir koʻrsatishga hech kim haqli emas.",
        "options": "A) 1,2,4\nB) 1,2,6\nC) 2,3,5\nD) 2,4,6",
        "correct_answer": "B",
        "block_id": 1
    },
    {
        "text": "5. Noto`g`ri mulohaza berilgan javobni toping. (Asos: 6-modda)",
        "options": "A) Referendum oʻtkaziladigan kunga qadar yoki referendum kunida 18 yoshga toʻlgan fuqaro referendumda ishtirok etish huquqiga ega.\nB) Oʻzbekiston Respublikasi hududidan tashqarida istiqomat qilayotgan fuqaro referendumda ishtirok etishga toʻla haqli.\nC) Sud tomonidan muomalaga layoqati cheklangan deb topilgan fuqarolar, shuningdek ozodlikdan mahrum etish joylarida saqlanayotgan shaxslar referendumda ishtirok etish huquqidan faqat qonunga muvofiq hamda sud qarori asosida mahrum etilishi mumkin.\nD) Kelib chiqishi, ijtimoiy va mulkiy mavqeyidan qat'i nazar fuqarolarning huquqlarini cheklash man etiladi.",
        "correct_answer": "C",
        "block_id": 1
    },
    {
        "text": "6. Quyidagilar orasidan to`g`ri mulohazalar berilgan javobni toping. (Asos: 7-8-moddalar)\n1) Referendumga tayyorgarlik koʻrish va uni oʻtkazishda davlat organlari va jamoat birlashmalari oʻz faoliyatlarini yopiq holatda amalga oshiradilar.\n2) Ommaviy axborot vositalari referendumga tayyorgarlikning borishi va u qanday oʻtayotganligini yoritib boradilar.\n3) Manfaatdor tashkilotlar, fuqarolar tashabbuskor guruhlari oʻz kuzatuvchilari toʻgʻrisida tegishli hududiy komissiyalarga referendum oʻtkazilishiga kechi bilan 10 kun qolganida maʼlum qiladilar.\n4) Hududiy komissiyalar ariza olganidan keyin 3 kun ichida mandatni kuzatuvchi uchun beradi.",
        "options": "A) 1,3\nB) 1,4\nC) 2,3\nD) 2,4",
        "correct_answer": "C",
        "block_id": 1
    },
    {
        "text": "7. Manfaatdor tashkilotlar, fuqarolar tashabbuskor guruhlari oʻz kuzatuvchilari toʻgʻrisida tegishli hududiy komissiyalarga referendum oʻtkazilishiga kechi bilan (a)-necha kun qolganida maʼlum qiladilar?\nHududiy komissiyalar ariza olganidan keyin (b)-necha kun ichida mandatni kuzatuvchi uchun beradi? (Asos: 8-modda)",
        "options": "A) a-1, b-3\nB) a-3, b-2\nC) a-2, b-4\nD) a-1, b-4",
        "correct_answer": "B",
        "block_id": 1
    },
    {
        "text": "8. Quyidagilar orasidan Noto`g`ri mulohaza berilgan javobni toping. (Asos: 10-modda)",
        "options": "A) Fuqarolar, jamoat birlashmalari referendum oʻtkazilishini yoqlab yoki unga qarshi moneliksiz tashviqot olib borishga haqlidirlar.\nB) Tashviqot olib borish maqsadida radio, televideniye va boshqa OAVlardan foydalanish mumkin.\nC) Tashviqotni fuqarolarga bepul yoki imtiyozli shartlarda tovarlar berish, xizmatlar koʻrsatish bilan qoʻshib olib borish taqiqlanadi.\nD) Referendum oʻtkaziladigan kunda va referendumni oʻtkazishga bir kun qolganda tashviqot yuritish mumkin.",
        "correct_answer": "D",
        "block_id": 1
    },
    {
        "text": "9. Quyidagilar orasidan referendum o`tkazish tashabbusi bilan chiqa oladigan subyektlar to`g`ri berilgan javobni toping. (Asos: 11-modda)\n1) Vazirlar Mahkamasi\n2) Oliy Majlis\n3) Bosh prokuror\n4) Prezident",
        "options": "A) 1,3\nB) 1,4\nC) 2,3\nD) 2,4",
        "correct_answer": "D",
        "block_id": 1
    },
    {
        "text": "10. Quyida keltirilgan ma’lumotlar bo`yicha so`nggi hukmni toping (To`g`ri//Noto`g`ri). (Asos: 12-13-moddalar)\nI. Fuqarolar umumiy sonining kamida 5 foizi imzosi toʻplangan boʻlsa...\nII. Kamida 50 kishidan iborat tashabbuskor guruh tuzilishi mumkin...\nIII. Vakolatli vakil MSKga ariza bilan murojaat etadi...\nIV. Referendumga qoʻyilayotgan masala matni referendum tayinlanganda maʼqullanadi...\nV. Referendum Prezident tomonidan tayinlanadi.",
        "options": "A) I-To`g`ri, II-To`g`ri, III-Noto`g`ri, IV-To`g`ri, V-Noto`g`ri\nB) I-To`g`ri, II-To`g`ri, III-To`g`ri, IV-To`g`ri, V-To`g`ri\nC) I-To`g`ri, II-Noto`g`ri, III-To`g`ri, IV-To`g`ri, V-Noto`g`ri\nD) I-To`g`ri, II-To`g`ri, III-To`g`ri, IV-To`g`ri, V-Noto`g`ri",
        "correct_answer": "D",
        "block_id": 1
    },
    {
        "text": "11. Quyida keltirilganlar orasidan referendum tayinlashga doir to`g`ri ma’lumotlar berilgan javobni toping. (Asos: 14-modda)",
        "options": "A) 1,3\nB) 1,4\nC) 2,3\nD) 2,4",
        "correct_answer": "D",
        "block_id": 1
    },
    {
        "text": "12. Referendum jarayonlaridagi hududiy komissiyalar qaysi davlat organi tomonidan tuziladi? (Asos: 19-modda)",
        "options": "A) Prezident\nB) Oliy Majlis\nC) Vazirlar Mahkamasi\nD) Markaziy saylov komissiyasi",
        "correct_answer": "D",
        "block_id": 1
    },
    {
        "text": "13. Referendum oʻtkazuvchi uchastka komissiyasi referendum tayinlash toʻgʻrisidagi qaror eʼlon qilinganidan keyin hududiy komissiya tomonidan necha kundan kechikmay tuziladi? (Asos: 21-modda)",
        "options": "A) Yigirma kun\nB) Yigirma besh kun\nC) O`n besh kun\nD) O`n kun",
        "correct_answer": "B",
        "block_id": 1
    },
    {
        "text": "14. Referendum o`tkazuvchi uchastka a’zolari necha nafardan iborat? (Asos: 21-modda)",
        "options": "A) Besh — oʻn toʻqqiz nafar\nB) Besh — oʻn nafar\nC) Yetti — oʻn besh nafar\nD) Uch — oʻn ikki nafar",
        "correct_answer": "A",
        "block_id": 1
    },
    {
        "text": "15. Referendum o`tkazuvchi uchastka komissiyasi a’zosi bo`lish uchun qo`yilgan talablar to`g`ri keltirilgan javobni toping. (Asos: 23-modda)\n1) 25 yoshga to`lgan fuqaro\n2) O`rta yoki oliy ma’lumotli shaxs\n3) Referendumgacha 10 yildan beri muqim yashayotgan fuqaro\n4) 21 yoshga toʻlgan fuqaro",
        "options": "A) 1,3\nB) 1,4\nC) 2,3\nD) 2,4",
        "correct_answer": "D",
        "block_id": 1
    },
    {
        "text": "16. Quyida keltirilgan ma’lumotlar bo`yicha so`nggi hukmni toping. (Asos: 24-modda)",
        "options": "A) I-Noto`g`ri, II-To`g`ri, III-To`g`ri, IV-Noto`g`ri, V-To`g`ri\nB) I-To`g`ri, II-To`g`ri, III-To`g`ri, IV-To`g`ri, V-To`g`ri\nC) I-To`g`ri, II-Noto`g`ri, III-To`g`ri, IV-To`g`ri, V-Noto`g`ri\nD) I-Noto`g`ri, II-To`g`ri, III-Noto`g`ri, IV-To`g`ri, V-To`g`ri",
        "correct_answer": "A",
        "block_id": 1
    },
    {
        "text": "17. Komissiya qarorlari ustidan (a)-necha kun ichida sudga va MSK qarorlari ustidan (b)-necha kun ichida Oliy sudga shikoyat qilinishi mumkin? (Asos: 25-modda)",
        "options": "A) a-1, b-3\nB) a-2, b-3\nC) a-2, b-2\nD) a-1, b-4",
        "correct_answer": "C",
        "block_id": 1
    },
    {
        "text": "18. Chet davlatlardagi fuqarolar ovoz beruvchi fuqarolar roʻyxatiga kiritish toʻgʻrisida referendumdan necha kun oldin murojaat qilishi mumkin? (Asos: 26¹-modda)",
        "options": "A) Yigirma kun\nB) Yigirma besh kun\nC) O`n besh kun\nD) O`n kun",
        "correct_answer": "C",
        "block_id": 1
    },
    {
        "text": "19. Ovoz beruvchi fuqarolarning roʻyxatlari ovoz berish kuniga necha kun qolganda hamma tanishishi uchun taqdim qilinadi? (Asos: 27-modda)",
        "options": "A) Yigirma kun\nB) Yigirma besh kun\nC) O`n besh kun\nD) O`n kun",
        "correct_answer": "D",
        "block_id": 1
    },
    {
        "text": "20. Referendum kunlarida ovoz berish qaysi vaqtlarda bo`lib o`tadi? (Asos: 32-modda)",
        "options": "A) 6.00 dan 20.00 gacha\nB) 8.00 dan 20.00 gacha\nC) 10.00 dan 22.00 gacha\nD) 6.00 dan 22.00 gacha",
        "correct_answer": "B",
        "block_id": 1
    },
    {
        "text": "21. Quyidagilar orasidan To`g`ri mulohaza berilgan javobni toping. (Asos: 35-modda)",
        "options": "A) 1,3\nB) 1,4\nC) 2,3\nD) 2,4",
        "correct_answer": "A",
        "block_id": 1
    },
    {
        "text": "22. Muddatidan oldin ovoz berish referendumga (a)-necha kun qolganida boshlanadi va (b)-necha kun qolganida tugallanadi? (Asos: 35¹-modda)",
        "options": "A) a-1, b-3\nB) a-2, b-3\nC) a-2, b-2\nD) a-3, b-1",
        "correct_answer": "D",
        "block_id": 1
    },
    {
        "text": "23. MSK referendum yakunlari boʻyicha qarorni koʻpi bilan necha kun ichida eʼlon qiladi? (Asos: 39-modda)",
        "options": "A) Yigirma kun\nB) Yigirma besh kun\nC) O`n besh kun\nD) O`n kun",
        "correct_answer": "D",
        "block_id": 1
    },
    {
        "text": "24. To`g`ri mulohazalar berilgan javobni toping. (Asos: 40-41-moddalar)",
        "options": "A) 1,3\nB) 1,4\nC) 2,3\nD) 2,4",
        "correct_answer": "A",
        "block_id": 1
    },
    {
        "text": "25. Referendumga oid ma’lumotlarning yakuniy xulosasi (to’g’ri/noto’g’ri) keltirilgan javobni aniqlang.",
        "options": "A) I-noto’g’ri, II-to’g’ri, III-noto’g’ri, IV-noto’g’ri, V-to’g’ri\nB) I-to’g’ri, II-noto’g’ri, III-to’g’ri, IV-to’g’ri, V-noto’g’ri\nC) I-to’g’ri, II-to’g’ri, III-noto’g’ri, IV-to’g’ri, V-noto’g’ri\nD) I-to’g’ri, II-to’g’ri, III-noto’g’ri, IV-noto’g’ri, V-noto’g’ri",
        "correct_answer": "D",
        "block_id": 1
    },
    {
        "text": "26. MSK referendum yakunlari bo’yicha qarorni necha kun ichida rasmiy manbalarda e’lon qiladi?",
        "options": "A) uch kun\nB) bir oy\nC) o’n kun\nD) uch oy",
        "correct_answer": "C",
        "block_id": 1
    },
    {
        "text": "27. Quyidagilar orasidan Noto`g`ri mulohaza berilgan javobni toping. (Asos: 26¹-modda)",
        "options": "A) Chet davlatlarda turgan fuqarolar 5 kun oldin yozma yoki elektron murojaat qilishi mumkin.\nB) Diplomatik vakolatxonalar murojaatni 3 kun ichida tekshiradi.\nC) TIV ma'lumotlarni darhol Davlat personallashtirish markaziga taqdim etadi.\nD) Diplomatik vakolatxonalar ma'lumotlarni darhol TIVga taqdim etadi.",
        "correct_answer": "A",
        "block_id": 1
    },
    {
        "text": "28. Quyidagilar orasidan To`g`ri mulohaza berilgan javobni toping. (Asos: 27-modda)",
        "options": "A) Ovoz beruvchilar roʻyxatiga oʻzgartish kiritish 5 kun qolganda toʻxtatiladi.\nB) Chet eldagi fuqarolarga IIV veb-sayti orqali imkoniyat yaratiladi.\nC) Statsionar muassasalarda ovoz berish kuniga 10 kun qolganida hamma tanishishi uchun taqdim qilinadi.\nD) Hududiy saylov komissiyasining rasmiy veb-sayti orqali ko'rish imkoniyati bor.",
        "correct_answer": "C",
        "block_id": 1
    },
    {
        "text": "29. Referendumda qabul qilingan qaror qaysi organ tomonidan referendum yakunlari rasmiy e’lon qilingan kundan e’tiboran kuchga kiradi?",
        "options": "A) O’zbekiston Respublikasi Oliy Majlisining Qonunchilik palatasi\nB) O’zbekiston Respublikasi Vazirlar Mahkamasi\nC) O’zbekiston Respublikasi Oliy Majlisining Senati\nD) O’zbekiston Respublikasi Markaziy saylov komissiyasi",
        "correct_answer": "D",
        "block_id": 1
    },
    {
        "text": "30. Referendum o’tkazish tashabbusi bilan chiqishi mumkin bo’lganlarni aniqlang.\n1. O’zbekiston Respublikasi fuqarolari\n2. Vazirlar Mahkamasi\n3. Oliy Majlis palatalari\n4. Prezident\n5. Markaziy saylov komissiyasi\n6. Huquqni muhofaza qiluvchi organlar",
        "options": "A) 1,2,4\nB) 2,3,5\nC) 1,4,5\nD) 1,3,4",
        "correct_answer": "D",
        "block_id": 1
    },
    {
        "text": "31. Referendum tayinlash to‘g‘risidagi qaror rasmiy e’lon qilingach, referendum qaysi muddat oralig'ida o‘tkazilishi kerak? (Asos: 14-modda)",
        "options": "A) 10 kundan keyin\nB) 1 oydan kam bo‘lmagan va 3 oydan oshmagan muddatda\nC) 6 oy ichida\nD) 1 yil ichida",
        "correct_answer": "B",
        "block_id": 1
    },
    {
        "text": "32. Markaziy saylov komissiyasi referendum oʻtkazuvchi hududiy komissiyalarni referendum tayinlangandan keyin necha kundan kechikmay tuzadi? (Asos: 19-modda)",
        "options": "A) 10 kun\nB) 15 kun\nC) 20 kun\nD) 25 kun",
        "correct_answer": "A",
        "block_id": 1
    },
    {
        "text": "33. Referendumda ovoz berish huquqiga ega bo'lgan fuqarolar ro'yxatiga har bir fuqaro necha marta kiritilishi mumkin? (Asos: 26-modda)",
        "options": "A) Faqat bir marta\nB) Ikki marta\nC) Cheklanmagan\nD) Yashash joyiga qarab bir nechta",
        "correct_answer": "A",
        "block_id": 1
    },
    {
        "text": "34. Ovoz berish binosida referendum kuni ovoz berish necha soatda to'xtatiladi? (Asos: 32-modda)",
        "options": "A) Soat 18:00 da\nB) Soat 20:00 da\nC) Soat 22:00 da\nD) Soat 24:00 da",
        "correct_answer": "B",
        "block_id": 1
    },
    {
        "text": "35. Referendum o'tkazuvchi komissiyalar faoliyatini moliyalashtirish qaysi manba hisobidan amalga oshiriladi? (Asos: 9-modda)",
        "options": "A) Homiylik xayriyalari\nB) Xususiy fondlar\nC) Oʻzbekiston Respublikasi Davlat bütjeti\nD) Xalqaro tashkilotlar grantlari",
        "correct_answer": "C",
        "block_id": 1
    },

    # ---------------- 10 TA OCHIQ TEST (Javobi matn/son) ----------------
    {
        "text": "36. Referendum o‘tkazish to‘g‘risida qaror qabul qiluvchi O‘zbekiston Respublikasining oliy vakillik organi qaysi?",
        "options": None,
        "correct_answer": "Oliy Majlis",
        "block_id": 1
    },
    {
        "text": "37. Referendum o‘tkaziladigan kuni fuqaro necha yoshga to‘lgan bo‘lsa, referendumda ishtirok etish huquqiga ega bo‘ladi?",
        "options": None,
        "correct_answer": "18",
        "block_id": 1
    },
    {
        "text": "38. Referendum natijalari e'lon qilingach, xuddi shunday savol bo'yicha referendum kamida necha yil davomida o'tkazilmaydi?",
        "options": None,
        "correct_answer": "1",
        "block_id": 1
    },
    {
        "text": "39. Fuqarolar referendum o'tkazish tashabbusi bilan chiqishi uchun kamida necha kishidan iborat tashabbuskor guruh tuzishi kerak?",
        "options": None,
        "correct_answer": "50",
        "block_id": 1
    },
    {
        "text": "40. Referendum o'tkazuvchi uchastka komissiyasi a'zolarining eng kam soni necha nafar bo'lishi kerak?",
        "options": None,
        "correct_answer": "5",
        "block_id": 1
    },
    {
        "text": "41. Referendum kunlarida ovoz berish soat nechada boshlanadi? (Format: 08:00 yoki 8:00)",
        "options": None,
        "correct_answer": "08:00",
        "block_id": 1
    },
    {
        "text": "42. Referendumda qabul qilingan qarorlar O'zbekiston Respublikasining butun hududida qanday yuridik kuchga ega?",
        "options": None,
        "correct_answer": "Oliy",
        "block_id": 1
    },
    {
        "text": "43. Muddatidan oldin ovoz berish referendumga necha kun qolganida tugallanadi?",
        "options": None,
        "correct_answer": "3",
        "block_id": 1
    },
    {
        "text": "44. Fuqarolar referendum o'tkazish tashabbusi huquqini amalga oshirishi uchun ovoz beruvchi fuqarolar umumiy sonining kamida necha foizi imzosi to'planishi kerak?",
        "options": None,
        "correct_answer": "5",
        "block_id": 1
    },
    {
        "text": "45. Referendum o'tkazuvchi uchastka komissiyasi a'zolarining eng ko'p soni necha nafar bo'lishi mumkin?",
        "options": None,
        "correct_answer": "19",
        "block_id": 1
    }
]

def seed_database():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Jadval mavjud bo'lmasa yaratish
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            text TEXT NOT NULL,
            options TEXT,
            correct_answer TEXT NOT NULL,
            block_id INTEGER DEFAULT 1
        )
    """)

    # Eski 1-blok savollarini tozalash (takrorlanib ketmasligi uchun)
    cursor.execute("DELETE FROM questions WHERE block_id = 1")

    # Yangi 45 ta savolni qo'shish
    count = 0
    for q in questions_data:
        cursor.execute("""
            INSERT INTO questions (text, options, correct_answer, block_id)
            VALUES (?, ?, ?, ?)
        """, (q["text"], q["options"], q["correct_answer"], q["block_id"]))
        count += 1

    conn.commit()
    conn.close()
    print(f"✅ 1-Blok uchun jami {count} ta savol (35 ta yopiq + 10 ta ochiq) muvaffaqiyatli bazaga qo'shildi!")

if __name__ == "__main__":
    seed_database()