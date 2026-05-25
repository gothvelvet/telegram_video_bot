import os
import yt_dlp
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = "8922515452:AAHdcnltBfwNXlDNPG6cKDmiakIJqbOfgvo"  # 👈 ВСТАВЬ ТОКЕН ОТ @BotFather!!!

# Папка для временных файлов
os.makedirs("downloads", exist_ok=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎬 Бот работает!\n\n"
        "Просто отправь ссылку на видео:\n"
        "• YouTube\n"
        "• TikTok\n"
        "• Instagram\n"
        "• VK\n"
        "• RuTube"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    user_id = update.message.from_user.id
    
    # Проверяем, что это ссылка на поддерживаемый сервис
    supported = ['youtube.com', 'youtu.be', 'tiktok.com', 'instagram.com', 'vk.com', 'rutube.ru']
    if not any(site in url for site in supported):
        await update.message.reply_text("❌ Отправь ссылку на видео с YouTube, TikTok, Instagram, VK или RuTube")
        return
    
    await update.message.reply_text("⏳ Скачиваю видео... Подожди немного")
    
    # Настройки для скачивания
    ydl_opts = {
        'format': 'best[height<=720]',  # Качество не выше 720p (экономит место)
        'outtmpl': f'downloads/{user_id}_video.%(ext)s',
        'quiet': True,
        'no_warnings': True,
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            
            # Проверяем размер файла (Telegram ограничение 50MB)
            file_size = os.path.getsize(filename)
            if file_size > 45 * 1024 * 1024:
                await update.message.reply_text("⚠️ Видео слишком большое (>50MB). Попробуй другое видео или ссылку на более короткое.")
                os.remove(filename)
                return
            
            # Отправляем видео
            with open(filename, 'rb') as f:
                await update.message.reply_video(f, caption="✅ Готово!")
            
            # Удаляем временный файл
            os.remove(filename)
            
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка: {str(e)[:150]}")
        # Очищаем временные файлы, если они есть
        for f in os.listdir("downloads"):
            if str(user_id) in f:
                try:
                    os.remove(f"downloads/{f}")
                except:
                    pass

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("🤖 Бот запущен и готов к работе на Render!")
    app.run_polling()

if __name__ == "__main__":
    main()