from telethon.sync import TelegramClient
from telethon import events
import asyncio

# تنظیمات حساب کاربری
api_id = 29071860  # api_id خود را وارد کنید
api_hash = 'f0290a2978eb718b6be68f04ca9271e3'  # api_hash خود را وارد کنید
phone = '+989172732771'  # شماره تلفن با فرمت +989123456789
destination_channel = -1002497670603  # آیدی کانال مقصد
source_channels = [
    -1001510759000, -1001953672462, -1001834171116, -1001973600729,
    -1001512524835, -1002358686814
]  # آیدی کانال‌های مبدأ

# ایجاد کلاینت تلگرام
client = TelegramClient('session_name', api_id, api_hash)

# متغیر برای شمارش پیام‌های فوروارد شده
forwarded_count = 0


@client.on(events.NewMessage(chats=source_channels))
async def handler(event):
    global forwarded_count
    try:
        # ابتدا سعی می‌کنیم پیام را فوروارد کنیم
        try:
            await client.forward_messages(destination_channel, event.message)
            forwarded_count += 1
            print(f"پیام فوروارد شد. تعداد کل: {forwarded_count}")
        except Exception as forward_error:
            print(f"فوروارد ممکن نیست، در حال کپی کردن پیام: {forward_error}")

            # اگر فوروارد نشد، پیام را کپی می‌کنیم
            message_text = event.message.text or ""

            # اگر پیام عکس دارد
            if event.message.photo:
                await client.send_file(destination_channel,
                                       event.message.photo,
                                       caption=message_text)
            # اگر پیام ویدیو دارد
            elif event.message.video:
                await client.send_file(destination_channel,
                                       event.message.video,
                                       caption=message_text)
            # اگر پیام فایل دارد
            elif event.message.document:
                await client.send_file(destination_channel,
                                       event.message.document,
                                       caption=message_text)
            # اگر پیام صوتی دارد
            elif event.message.voice:
                await client.send_file(destination_channel,
                                       event.message.voice,
                                       caption=message_text)
            # اگر فقط متن دارد
            elif message_text:
                await client.send_message(destination_channel, message_text)

            forwarded_count += 1
            print(f"پیام کپی شد. تعداد کل: {forwarded_count}")

    except Exception as e:
        print(f"خطا در ارسال پیام: {e}")


# وب سرور handlers
async def status_handler(request):
    return web.json_response({
        'status': 'Bot is running',
        'forwarded_messages': forwarded_count,
        'source_channels': len(source_channels),
        'destination_channel': destination_channel
    })


async def home_handler(request):
    html = f"""
    <!DOCTYPE html>
    <html dir="rtl">
    <head>
        <meta charset="utf-8">
        <title>ربات فوروارد تلگرام</title>
        <style>
            body {{ font-family: Arial; text-align: center; padding: 50px; }}
            .status {{ background: #e8f5e8; padding: 20px; border-radius: 10px; margin: 20px 0; }}
        </style>
    </head>
    <body>
        <h1>ربات فوروارد تلگرام</h1>
        <div class="status">
            <h2>وضعیت ربات: فعال ✅</h2>
            <p>تعداد پیام‌های فوروارد شده: {forwarded_count}</p>
            <p>تعداد کانال‌های مبدأ: {len(source_channels)}</p>
        </div>
        <p>این ربات پیام‌هایی از کانال‌های مبدأ را به کانال مقصد فوروارد می‌کند.</p>
    </body>
    </html>
    """
    return web.Response(text=html, content_type='text/html')


async def create_web_app():
    app = web.Application()
    app.router.add_get('/', home_handler)
    app.router.add_get('/status', status_handler)
    return app


# تابع نگه‌داشتن ربات زنده
async def keep_alive():
    while True:
        try:
            await asyncio.sleep(300)  # هر 5 دقیقه
            print("ربات زنده است...")
        except Exception as e:
            print(f"خطا در keep-alive: {e}")


# راه‌اندازی ربات
async def main():
    print("ربات شروع به کار کرد...")

    try:
        # شروع کلاینت تلگرام
        await client.start(phone)
        print("کلاینت تلگرام متصل شد")

        # ایجاد وب اپلیکیشن
        app = await create_web_app()

        # راه‌اندازی وب سرور
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, '0.0.0.0', 5000)
        await site.start()
        print("وب سرور در پورت 5000 راه‌اندازی شد")

        # شروع keep-alive task
        keep_alive_task = asyncio.create_task(keep_alive())

        # اجرای ربات تا زمان قطع اتصال
        await client.run_until_disconnected()

    except Exception as e:
        print(f"خطا در اجرای ربات: {e}")
        await asyncio.sleep(10)
        # تلاش مجدد
        await main()


if __name__ == "__main__":
    while True:
        try:
            asyncio.run(main())
        except Exception as e:
            print(f"ربات متوقف شد: {e}")
            print("تلاش مجدد در 30 ثانیه...")
            asyncio.sleep(30)
