import sys
import os
from database import SessionLocal, Question

def seed_database():
    db = SessionLocal()

    questions_data = [
        {
            "text": "Quyidagilar orasidan Noto`g`ri mulohaza berilgan javobni toping. (Asos: “O`zbekiston Respublikasi referendum to`g`risida”gi qonun 1-modda)",
            "a": "Oʻzbekiston Respublikasining referendumi Oʻzbekiston Respublikasining qonunlarini va boshqa qarorlarni qabul qilish maqsadlarida jamiyat va davlat hayotining eng muhim masalalari yuzasidan fuqarolarning umumxalq ovoz berishidir.",
            "b": "Referendum saylovlar bilan bir qatorda xalq irodasining bevosita ifodasidir.",
            "c": "Agar referendumda qabul qilingan qarorlarda boshqacha tartib nazarda tutilgan boʻlmasa, referendumda qabul qilingan qarorlar faqat referendum yoʻli bilan bekor qilinishi yoki oʻzgartirilishi mumkin.",
            "d": "Referendumda qabul qilingan qarorlar oliy yuridik kuchga ega emas.",
            "correct": "D"
        },
        {
            "text": "Quyidagilar orasidan referendum predmeti bo`la olmaydigan masalalar to`g`ri keltirilgan javobni toping. (Asos: 2-modda)\n1) Hududiy yaxlitlikni oʻzgartirish\n2) Chet elga ijtimoiy yordam berish\n3) Amnistiya va afv etish\n4) Konstitutsiyaga oʻzgartirish va qoʻshimchalar kiritish",
            "a": "1,3",
            "b": "1,4",
            "c": "2,3",
            "d": "2,4",
            "correct": "A"
        },
        {
            "text": "Oʻzbekiston Respublikasining butun hududida joriy etilgan harbiy vaqt yoki favqulodda holat sharoitlarida, shuningdek harbiy vaqt tugagan yoki favqulodda holat bekor qilingandan keyin (a)-qancha muddat davomida referendum oʻtkazilmaydi?\nReferendum natijalari rasman eʼlon qilingandan keyin (b)-qancha muddat davomida mazmun yoki maʼnosiga koʻra xuddi shunday savol qoʻyilgan referendum oʻtkazilmaydi?\n1) Bir oy  2) Uch oy  3) Olti oy  4) Bir yil",
            "a": "a-2, b-3",
            "b": "a-1, b-3",
            "c": "a-2, b-4",
            "d": "a-1, b-4",
            "correct": "D"
        },
        {
            "text": "To`g`ri mulohazalar berilgan javobni toping. (Asos: 5-modda)\n1) Referendum fuqarolarning oʻz xohish-irodasini umumiy, teng va toʻgʻridan-toʻgʻri bildirishi asosida yashirin ovoz berish yoʻli bilan oʻtkaziladi.\n2) Fuqarolar referendumda teng asoslarda ishtirok etadilar.\n3) Fuqarolarning referendumda ishtirok etishi majburiy.\n4) Fuqarolarning oʻz xohish-irodasini bildirishi nazorat qilinishiga yoʻl qoʻyiladi.\n5) Fuqarolar referendumda vakillari bilan birga ishtirok etadi.\n6) Fuqarolarni referendumda ishtirok etishga yoki ishtirok etmaslikka majbur qilish maqsadida ularga taʼsir koʻrsatishga hech kim haqli emas.",
            "a": "1,2,4",
            "b": "1,2,6",
            "c": "2,3,5",
            "d": "2,4,6",
            "correct": "B"
        },
        {
            "text": "Noto`g`ri mulohaza berilgan javobni toping. (Asos: 6-modda)",
            "a": "Referendum oʻtkaziladigan kunga qadar yoki referendum kunida oʻn sakkiz yoshga toʻlgan Oʻzbekiston Respublikasining har bir fuqarosi referendumda ishtirok etish huquqiga egadir.",
            "b": "Oʻzbekiston Respublikasi hududidan tashqarida istiqomat qilayotgan yoki turgan Oʻzbekiston Respublikasining fuqarosi referendumda ishtirok etishga toʻla haqlidir.",
            "c": "Sud tomonidan muomalaga layoqati cheklangan deb topilgan fuqarolar, shuningdek ijtimoiy xavfi katta bo`lmagan va uncha ogʻir bo`lmagan jinoyatlar sodir etganlik uchun sudning hukmiga koʻra ozodlikdan mahrum etish joylarida saqlanayotgan shaxslar referendumda ishtirok etish huquqidan faqat qonunga muvofiq hamda sudning qarori asosida mahrum etilishi mumkin.",
            "d": "Kelib chiqishi, ijtimoiy va mulkiy mavqeyi, irqiy va milliy mansubligi, jinsi, maʼlumoti, tili, dinga munosabati, mashgʻulotining turi va xususiyatiga qarab fuqarolarning referendumda qatnashish huquqlarini bevosita yoki bilvosita cheklash man etiladi.",
            "correct": "C"
        },
        {
            "text": "Quyidagilar orasidan to`g`ri mulohazalar berilgan javobni toping. (Asos: 7-8-moddalar)\n1) Referendumga tayyorgarlik koʻrish va uni oʻtkazishda qatnashayotgan davlat organlari oʻz faoliyatlarini yopiq holatda amalga oshiradilar.\n2) Ommaviy axborot vositalari referendumga tayyorgarlikning borishi va u qanday oʻtayotganligini yoritib boradilar.\n3) Kuzatuvchilar toʻgʻrisida tegishli hududiy komissiyalarga kechi bilan oʻn kun qolganida maʼlum qilinadi.\n4) Hududiy komissiyalar ariza olganidan keyin uch kun ichida mandatni kuzatuvchi uchun beradi.",
            "a": "1,3",
            "b": "1,4",
            "c": "2,3",
            "d": "2,4",
            "correct": "D"
        },
        {
            "text": "Manfaatdor tashkilotlar, fuqarolar tashabbuskor guruhlari oʻz kuzatuvchilari toʻgʻrisida tegishli hududiy komissiyalarga referendum oʻtkazilishiga kechi bilan (a)-necha kun qolganida maʼlum qiladilar.\nHududiy komissiyalar ariza olganidan keyin (b)-necha kun ichida mandatni kuzatuvchi uchun beradi.\n1) Uch kun  2) Besh kun  3) O`n kun  4) O`n besh kun",
            "a": "a-1, b-3",
            "b": "a-3, b-2",
            "c": "a-2, b-4",
            "d": "a-1, b-4",
            "correct": "C"
        },
        {
            "text": "Quyidagilar orasidan Noto`g`ri mulohaza berilgan javobni toping. (Asos: 10-modda)",
            "a": "Fuqarolar, jamoat birlashmalari referendum oʻtkazilishini yoqlab yoki unga qarshi moneliksiz tashviqot olib borishga haqlidirlar.",
            "b": "Tashviqot olib borish maqsadida radio, televideniye va boshqa OAVlardan foydalanish mumkin.",
            "c": "Tashviqotni fuqarolarga bepul yoki imtiyozli shartlarda tovarlar berish, xizmatlar koʻrsatish bilan qoʻshib olib borish taqiqlanadi.",
            "d": "Referendum oʻtkaziladigan kunda va referendumni oʻtkazishga bir kun qolganda tashviqot yuritish mumkin.",
            "correct": "D"
        },
        {
            "text": "Quyidagilar orasidan referendum o`tkazish tashabbusi bilan chiqa oladigan subyektlar to`g`ri berilgan javobni toping. (Asos: 11-modda)\n1) Vazirlar Mahkamasi\n2) Oliy Majlis\n3) Bosh prokuror\n4) Prezident",
            "a": "1,3",
            "b": "1,4",
            "c": "2,3",
            "d": "2,4",
            "correct": "D"
        },
        {
            "text": "Quyida keltirilgan ma’lumotlar bo`yicha so`nggi hukmni toping (To`g`ri/Noto`g`ri):\nI. Fuqarolar referendumda ishtirok etish huquqiga ega fuqarolar umumiy sonining kamida 5 foizi imzo to'plagan bo'lsa tashabbus ko'rsatadi.\nII. Tashabbuskor guruh kamida 50 kishidan iborat bo'lishi mumkin.\nIII. Vakolatli vakil guruhni ro'yxatdan o'tkazish uchun MSKga murojaat qiladi.\nIV. Masala matni referendum tayinlanganda ma'qullanadi.\nV. Referendum Prezident tomonidan tayinlanadi.",
            "a": "I-To`g`ri, II-To`g`ri, III-Noto`g`ri, IV-To`g`ri, V-Noto`g`ri",
            "b": "I-To`g`ri, II-To`g`ri, III-To`g`ri, IV-To`g`ri, V-To`g`ri",
            "c": "I-To`g`ri, II-Noto`g`ri, III-To`g`ri, IV-To`g`ri, V-Noto`g`ri",
            "d": "I-To`g`ri, II-To`g`ri, III-Noto`g`ri, IV-To`g`ri, V-To`g`ri",
            "correct": "A"
        },
        {
            "text": "Quyida keltirilganlar orasidan referendum tayinlashga doir to`g`ri ma’lumotlar berilgan javobni toping. (Asos: 14-modda)\n1) Qonunchilik palatasi materiallarni ikki hafta ichida koʻrib chiqib qaror chiqarishi mumkin.\n2) Qonunchilik palatasining qarori 5 kun ichida Senatga yuboriladi.\n3) Rad etilsa, ayni shu masala 6 oy oʻtganidan keyingina takroran kiritilishi mumkin.\n4) Senat materiallarni ikki hafta ichida koʻrib chiqib qaror chiqarishi mumkin.",
            "a": "1,3",
            "b": "1,4",
            "c": "2,3",
            "d": "2,4",
            "correct": "B"
        },
        {
            "text": "Referendum jarayonlaridagi hududiy komissiyalar qaysi davlat organi tomonidan tuziladi? (Asos: 19-modda)",
            "a": "Prezident",
            "b": "Oliy Majlis",
            "c": "Vazirlar Mahkamasi",
            "d": "Markaziy saylov komissiyasi",
            "correct": "D"
        },
        {
            "text": "Referendum oʻtkazuvchi uchastka komissiyasi referendum tayinlash toʻgʻrisidagi qaror eʼlon qilinganidan keyin hududiy komissiya tomonidan necha kundan kechikmay tuziladi? (Asos: 21-modda)",
            "a": "Yigirma kun",
            "b": "Yigirma besh kun",
            "c": "O`n besh kun",
            "d": "O`n kun",
            "correct": "B"
        },
        {
            "text": "Referendum o`tkazuvchi uchastka a’zolari necha nafardan iborat? (Asos: 21-modda)",
            "a": "Besh — oʻn toʻqqiz nafar",
            "b": "Besh — oʻn nafar",
            "c": "Yetti — oʻn besh nafar",
            "d": "Uch — oʻn ikki nafar",
            "correct": "A"
        },
        {
            "text": "Referendum o`tkazuvchi uchastka komissiyasi a’zosi bo`lish uchun qo`yilgan talablar to`g`ri keltirilgan javobni toping. (Asos: 23-modda)\n1) 25 yoshga to'lgan fuqaro\n2) O'rta yoki oliy ma'lumotli shaxs\n3) O'zbekistonda 10 yil muqim yashayotgan fuqaro\n4) 21 yoshga toʻlgan fuqaro",
            "a": "1,3",
            "b": "1,4",
            "c": "2,3",
            "d": "2,4",
            "correct": "D"
        },
        {
            "text": "Quyida keltirilgan ma’lumotlar bo`yicha so`nggi hukmni toping (To`g`ri/Noto`g`ri) (Asos: 24-modda):\nI. Majlisda tarkibning ko'pchilik qismi ishtirok etsa vakolatli hisoblanadi.\nII. Komissiya qarori umumiy tarkibning ko'pchilik ovozi bilan qabul qilinadi.\nIII. Ovozlar teng bo'lsa, raislik qiluvchining ovozi hal qiluvchi bo'ladi.\nIV. Komissiya a'zolariga xarajatlar kompensatsiya qilib to'lab berilmaydi.\nV. Uchastka komissiyalari natijalar e'lon qilingach faoliyatini tugatadi.",
            "a": "I-Noto`g`ri, II-To`g`ri, III-To`g`ri, IV-Noto`g`ri, V-To`g`ri",
            "b": "I-To`g`ri, II-To`g`ri, III-To`g`ri, IV-To`g`ri, V-To`g`ri",
            "c": "I-To`g`ri, II-Noto`g`ri, III-To`g`ri, IV-To`g`ri, V-Noto`g`ri",
            "d": "I-Noto`g`ri, II-To`g`ri, III-Noto`g`ri, IV-To`g`ri, V-To`g`ri",
            "correct": "A"
        },
        {
            "text": "Fuqarolar va kuzatuvchilar komissiya qarorlari ustidan (a)-necha kun ichida sudga shikoyat qilishi mumkin? MSK qarorlari ustidan qaror qabul qilingach (b)-necha kun ichida Oliy sudga shikoyat qilinadi? (Asos: 25-modda)\n1) Uch kun  2) Besh kun  3) O'n kun  4) O'n besh kun",
            "a": "a-1, b-3",
            "b": "a-2, b-3",
            "c": "a-2, b-2",
            "d": "a-1, b-4",
            "correct": "C"
        },
        {
            "text": "Chet davlatlarda turgan fuqarolar diplomatik vakolatxonalar huzuridagi uchastka komissiyalariga ularni ro'yxatga kiritish to'g'risida referendumdan necha kun oldin murojaat qilishi mumkin? (Asos: 261-modda)",
            "a": "Yigirma kun",
            "b": "Yigirma besh kun",
            "c": "O`n besh kun",
            "d": "O`n kun",
            "correct": "C"
        },
        {
            "text": "Ovoz beruvchi fuqarolarning roʻyxatlari ovoz berish kuniga necha kun qolganda hamma tanishishi uchun taqdim qilinadi? (Asos: 27-modda)",
            "a": "Yigirma kun",
            "b": "Yigirma besh kun",
            "c": "O`n besh kun",
            "d": "O`n kun",
            "correct": "D"
        },
        {
            "text": "Referendum kunlarida ovoz berish qaysi vaqtlarda bo`lib o`tadi? (Asos: 32-modda)",
            "a": "6.00 dan 20.00 gacha",
            "b": "8.00 dan 20.00 gacha",
            "c": "10.00 dan 22.00 gacha",
            "d": "6.00 dan 22.00 gacha",
            "correct": "B"
        },
        {
            "text": "Quyidagilar orasidan To`g`ri mulohaza berilgan javobni toping. (Asos: 35-modda)\n1) Byulleten yashirin ovoz berish kabinasida toʻldiriladi.\n2) Byulletenni mustaqil toʻldira olmagan fuqaro boshqa shaxsni taklif qilishga haqli emas.\n3) Ovoz berish binosiga kela olmaganlarga turgan joyida ovoz berish tashkil etiladi.\n4) Komissiyaning kamida 4 nafar a'zosi ko'chma quti bilan yuboriladi.",
            "a": "1,3",
            "b": "1,4",
            "c": "2,3",
            "d": "2,4",
            "correct": "A"
        },
        {
            "text": "Muddatidan oldin ovoz berish referendumga (a)-necha kun qolganida boshlanadi va referendumga (b)-necha kun qolganida tugallanadi? (Asos: 351-modda)\n1) Uch kun  2) Besh kun  3) O'n kun  4) O'n besh kun",
            "a": "a-1, b-3",
            "b": "a-2, b-3",
            "c": "a-2, b-2",
            "d": "a-3, b-1",
            "correct": "D"
        },
        {
            "text": "MSK referendum yakunlari boʻyicha qarorni referendum oʻtkazilgandan keyin koʻpi bilan necha kun ichida rasmiy manbalarda eʼlon qiladi? (Asos: 39-modda)",
            "a": "Yigirma kun",
            "b": "Yigirma besh kun",
            "c": "O`n besh kun",
            "d": "O`n kun",
            "correct": "D"
        },
        {
            "text": "To`g`ri mulohazalar berilgan javobni toping. (Asos: 40-41-moddalar)\n1) Referendum qarori rasmiy eʼlon qilingan kunning oʻzida Oliy Majlis palatalariga va Prezidentga yuboriladi.\n2) Qaror davlat hokimiyati organlarining hujjatlari bilan biron-bir tarzda tasdiqlanishi talab etiladi.\n3) Qonunlar referendum qaroriga muvofiqlashtirilmogʻi lozim.\n4) Hujjatlar ro'yxati yigirma kun ichida belgilanishi shart.",
            "a": "1,3",
            "b": "1,4",
            "c": "2,3",
            "d": "2,4",
            "correct": "A"
        },
        {
            "text": "O’zbekiston Respublikasi referendumiga oid ma’lumotlarning yakuniy xulosasi (to’g’ri/noto’g’ri):\nI. Harbiy/favqulodda holatda referendum o'tkazilmaydi;\nII. Umumiy, teng, to'g'ridan-to'g'ri, yashirin ovoz berish yo'li bilan o'tkaziladi;\nIII. Referendum Prezident tomonidan tayinlanadi;\nIV. Byulletenda nomzodning ism-familiyasi ko'rsatiladi;\nV. Ovoz berish soat 6:00 dan 18:00 gacha o'tkaziladi.",
            "a": "I-noto’g’ri, II-to’g’ri, III-noto’g’ri, IV-noto’g’ri, V-to’g’ri",
            "b": "I-to’g’ri, II-noto’g’ri, III-to’g’ri, IV-to’g’ri, V-noto’g’ri",
            "c": "I-to’g’ri, II-to’g’ri, III-noto’g’ri, IV-to’g’ri, V-noto’g’ri",
            "d": "I-to’g’ri, II-to’g’ri, III-noto’g’ri, IV-noto’g’ri, V-noto’g’ri",
            "correct": "D"
        },
        {
            "text": "MSK referendum yakunlari bo’yicha qabul qilingan qarorni referendum o’tkazilgandan keyin ko’pi bilan qancha vaqt ichida e’lon qiladi?",
            "a": "uch kun",
            "b": "bir oy",
            "c": "o’n kun",
            "d": "uch oy",
            "correct": "C"
        },
        {
            "text": "Quyidagilar orasidan Noto`g`ri mulohaza berilgan javobni toping. (Asos: 261-modda)",
            "a": "Chet davlatlardagi fuqarolar ro'yxatga kiritish to'g'risida referendumdan besh kun oldin murojaat qilishi mumkin.",
            "b": "Vakolatxona komissiyalari murojaatdagi ma'lumotlarni uch kun ichida tekshiradi.",
            "c": "TIV ma'lumotlarni darhol Davlat personallashtirish markaziga taqdim etadi.",
            "d": "Vakolatxona komissiyalari ma'lumotlarni darhol TIVga taqdim etadi.",
            "correct": "A"
        },
        {
            "text": "Quyidagilar orasidan To`g`ri mulohaza berilgan javobni toping. (Asos: 27-modda)",
            "a": "Ovoz beruvchilar roʻyxatiga oʻzgartish kiritish referendumga besh kun qolganida toʻxtatiladi.",
            "b": "Chet eldagi fuqarolarga ro'yxat bilan tanishish IIV va TIV rasmiy veb-saytlari orqali taʼminlanadi.",
            "c": "Davolash muassasalarida tuzilgan uchastkalarda ovoz berish kuniga o’n kun qolganida taqdim qilinadi.",
            "d": "Hududiy saylov komissiyasining rasmiy veb-sayti orqali tanishish imkoniyati taʼminlanadi.",
            "correct": "B"
        },
        {
            "text": "Agar referendumda qabul qilingan qarorning mazmunidan boshqacha qoida kelib chiqmasa, referendumda qabul qilingan qaror .... tomonidan rasmiy e’lon qilingan kundan e’tiboran kuchga kiradi.",
            "a": "O’zbekiston Respublikasi Oliy Majlisining Qonunchilik palatasi",
            "b": "O’zbekiston Respublikasi Vazirlar Mahkamasi",
            "c": "O’zbekiston Respublikasi Oliy Majlisining Senati",
            "d": "O’zbekiston Respublikasi Markaziy saylov komissiyasi",
            "correct": "D"
        },
        {
            "text": "Quyidagilardan Referendum o’tkazish tashabbusi bilan chiqishi mumkin bo’lganlarini aniqlang:\n1. O’zbekiston Respublikasi fuqarolari\n2. Vazirlar Mahkamasi\n3. Oliy Majlis palatalari\n4. O’zbekiston Respublikasi Prezidenti\n5. Markaziy saylov komissiyasi\n6. Huquqni muhofaza qiluvchi organlar",
            "a": "1,2,4",
            "b": "2,3,5",
            "c": "1,4,5",
            "d": "1,3,4",
            "correct": "D"
        }
    ]

    added_count = 0
    skipped_count = 0

    try:
        for item in questions_data:
            # Duplikat savollar takroran qo'shilmasligi uchun tekshirish
            exists = db.query(Question).filter_by(text=item["text"]).first()
            if not exists:
                q = Question(
                    text=item["text"],
                    option_a=item["a"],
                    option_b=item["b"],
                    option_c=item["c"],
                    option_d=item["d"],
                    correct_answer=item["correct"]
                )
                db.add(q)
                added_count += 1
            else:
                skipped_count += 1

        db.commit()
        print(f"✅ Baza muvaffaqiyatli to'ldirildi!")
        print(f"➕ Qo'shildi: {added_count} ta savol")
        print(f"⏩ Avvaldan bor (o'tkazib yuborildi): {skipped_count} ta savol")
    except Exception as e:
        db.rollback()
        print(f"❌ Xatolik yuz berdi: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()