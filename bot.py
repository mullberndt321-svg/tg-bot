import os
import subprocess
import tempfile
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler
import yt_dlp

# Logging aktivieren
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Trage hier deinen Bot-Token ein
TOKEN = "8091232458:AAGaP5Vh8mtueiJ3yBaST1BfcxvcDEm1S74"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start-Nachricht mit Anleitung."""
    await update.message.reply_text(
        "👋 Hallo! Ich bin dein Medien-Downloader Bot.\n\n"
        "Verwende folgende Befehle:\n"
        "🎥 /mp4 <YouTube-Link> - Lädt ein YouTube-Video als MP4 herunter\n"
        "🎵 /mp3 <YouTube-Link> - Lädt YouTube-Audio als MP3 herunter\n"
        "🎧 /spotify <Spotify-Link> - Lädt einen Spotify-Song als MP3 herunter"
    )

async def download_youtube_mp4(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """YouTube Video als MP4 herunterladen"""
    if not context.args:
        await update.message.reply_text("❌ Bitte gib einen Link an:\nBeispiel: `/mp4 https://youtube.com/watch?v=...`", parse_mode="Markdown")
        return
    
    url = context.args[0]
    status_msg = await update.message.reply_text("⏳ Lade YouTube-Video als MP4 herunter...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        ydl_opts = {
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'outtmpl': os.path.join(temp_dir, '%(title)s.%(ext)s'),
            'max_filesize': 50 * 1024 * 1024,
            'cookiefile': 'cookies.txt',  # Nutzt die hochgeladene Cookie-Datei
        }
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)
            
            with open(filename, 'rb') as video_file:
                await update.message.reply_document(document=video_file)
                
            await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=status_msg.message_id)
        except Exception as e:
            await update.message.reply_text(f"❌ Fehler beim Download: {str(e)}")

async def download_youtube_mp3(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """YouTube Video als MP3 Audio herunterladen"""
    if not context.args:
        await update.message.reply_text("❌ Bitte gib einen Link an:\nBeispiel: `/mp3 https://youtube.com/watch?v=...`", parse_mode="Markdown")
        return
        
    url = context.args[0]
    status_msg = await update.message.reply_text("⏳ Lade YouTube-Audio als MP3 herunter...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'outtmpl': os.path.join(temp_dir, '%(title)s.%(ext)s'),
            'cookiefile': 'cookies.txt',  # Nutzt die hochgeladene Cookie-Datei
        }
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)
                base, _ = os.path.splitext(filename)
                mp3_filename = base + ".mp3"
                
            with open(mp3_filename, 'rb') as audio_file:
                await update.message.reply_audio(audio=audio_file)
                
            await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=status_msg.message_id)
        except Exception as e:
            await update.message.reply_text(f"❌ Fehler beim Download: {str(e)}")

async def download_spotify(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Spotify Track als MP3 herunterladen (via spotdl)"""
    if not context.args:
        await update.message.reply_text("❌ Bitte gib einen Spotify-Link an:\nBeispiel: `/spotify https://open.spotify.com/track/...`", parse_mode="Markdown")
        return
        
    url = context.args[0]
    status_msg = await update.message.reply_text("⏳ Suche und lade Spotify-Titel herunter (via spotdl)...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        try:
            result = subprocess.run(['spotdl', 'download', url], cwd=temp_dir, capture_output=True, text=True)
            
            if result.returncode != 0:
                error_msg = result.stderr.strip() or result.stdout.strip()
                raise Exception(f"spotdl-Fehler: {error_msg[-300:]}")
                
            mp3_files = [os.path.join(temp_dir, f) for f in os.listdir(temp_dir) if f.endswith('.mp3')]
            if not mp3_files:
                raise Exception("Es konnte keine MP3-Datei generiert werden.")
                
            audio_file = mp3_files[0]
            
            with open(audio_file, 'rb') as f:
                await update.message.reply_audio(audio=f)
                
            await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=status_msg.message_id)
        except Exception as e:
            await update.message.reply_text(f"❌ {str(e)}")

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("mp4", download_youtube_mp4))
    app.add_handler(CommandHandler("mp3", download_youtube_mp3))
    app.add_handler(CommandHandler("spotify", download_spotify))
    
    print("🤖 Bot gestartet und bereit...")
    app.run_polling()

if __name__ == '__main__':
    main()