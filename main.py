from telethon.sync import TelegramClient, events
import asyncio
import base64
import os
import re
from getpass import getpass

# استرجاع بيانات الجلسة المشفرة من متغير البيئة وفكها
session_data = os.getenv("SESSION_DATA")
if session_data:
    with open("session_name.session", "wb") as f:
        decoded_data = base64.b64decode(session_data)
        f.write(decoded_data)
        print("✅ تم فك التشفير وحفظ الجلسة بنجاح!")

# إعدادات API و التليجرام
api_id = 26283926
api_hash = 'fcd8c080125fad9062c9bc7d9cb2ca2d'
source_channel = -1002304519486
destination_bot = 'TradeWiz_Solbot'

client = TelegramClient('session_name', api_id, api_hash)

# دالة استخراج العقد وإرساله فقط (بسرعة)
@client.on(events.NewMessage(chats=source_channel))
async def forward_contract_only(event):
    try:
        # محاولة جلب النص من أكثر من مصدر (للتعامل مع الرسائل العادية والموجهة)
        raw_text = event.message.message or event.message.raw_text or ""
    except Exception:
        raw_text = ""

    if not raw_text.strip():
        print("⚠️ لا يوجد نص يمكن تحليله.")
        return

    print(f"📩 النص المستلم:\n{raw_text}")

    # استخراج أول سطر يحتوي على عقد بالشكل المعروف
    lines = raw_text.splitlines()
    contract = None
    for line in lines:
        if re.match(r"^[a-zA-Z0-9]{30,}pump$", line.strip()):
            contract = line.strip()
            break

    if contract:
        print(f"✅ تم استخراج العقد: {contract}")
        try:
            await client.send_message(destination_bot, contract)
            print("📤 تم إرسال العقد للبوت.")
        except Exception as e:
            print(f"❌ خطأ أثناء الإرسال: {e}")
    else:
        print("⚠️ لم يتم العثور على عقد في الرسالة.")

# دالة إعادة الاتصال التلقائي إذا انقطع
async def restart_client():
    while True:
        try:
            print("🔄 جاري إعادة الاتصال بتليغرام...")
            await client.connect()
            if not await client.is_user_authorized():
                print("❗ الجلسة غير مصرح بها. تسجيل الدخول الآن...")
                phone = input("📱 أدخل رقم الهاتف مع رمز الدولة (مثلاً +201234567890): ")
                await client.send_code_request(phone)
                code = input("📨 أدخل كود التحقق الذي وصلك: ")
                try:
                    await client.sign_in(phone, code)
                except Exception as e:
                    if "password" in str(e).lower():
                        password = getpass("🔐 الحساب محمي بكلمة سر. أدخل كلمة المرور: ")
                        try:
                            await client.sign_in(password=password)
                        except Exception as e2:
                            print(f"⚠️ فشل تسجيل الدخول بعد إدخال كلمة السر: {e2}")
                            return
                    else:
                        print(f"⚠️ فشل تسجيل الدخول: {e}")
                        return
            print("✅ تم الاتصال بنجاح!")
            await client.run_until_disconnected()
        except Exception as e:
            print(f"🚫 فشل الاتصال، إعادة المحاولة بعد 5 ثوانٍ... {e}")
            await asyncio.sleep(5)

print("🚀 البوت يعمل الآن، في انتظار الرسائل...")
client.loop.run_until_complete(restart_client())
