import logging
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
from moviepy.editor import VideoFileClip

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Hello, my name is Михаил Круг, please send me your video!")
async def message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="send me video!!")

async def video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file_id = update.message.video.file_id
    video = download_video(file_id)
    output_video = make_video_square(video)
    
    try:
        with open(output_video, 'rb') as video_note:
            await context.bot.send_video_note(
                chat_id=update.effective_chat.id,
                video_note=video_note
                )
    except Exception as e:
        await context.bot.send_message(
            chat_id = update.effective_chat.id,
            text=f"Error: {str(e)}")

def download_video(file_id):
    file_source = get_video_file_source(file_id)
    return get_file(file_source)

def get_video_file_source(file_id):
    url = f'https://api.telegram.org/bot6823760649:AAGPR6MCvHEv-QRimKjrz3K_DBSt5EpLqi0/getFile'
    params = {'file_id': file_id}
    response = requests.get(url, params=params)
    
    if response.status_code == 200 and 'result' in response.json():
        file_source = response.json()['result']['file_path']
        return file_source
    else:
        error_message = response.json().get('description', 'Unknown error occurred.')
        raise Exception(f"Error getting file source: {error_message}")

def get_file(file_source):
    url = 'https://api.telegram.org/file/bot' + '6823760649:AAGPR6MCvHEv-QRimKjrz3K_DBSt5EpLqi0' + '/' + file_source
    r = requests.get(url)
    filename = 'Video.mp4'
    try:
        with open(filename, 'wb') as file:
            file.write(r.content)
        return filename
    except:
        return 'there are something wrong'

def make_video_square(video):
    clip = VideoFileClip(video)
    w, h = clip.size
    min_size = min(w, h)
    clip = clip.crop(x_center=w/2, y_center=h/2, width=min_size, height=min_size)
    output_path = 'squared_video.mp4'
    clip_resized = clip.resize((639, 639))
    clip_resized.write_videofile(output_path, codec='libx264')
    return output_path

async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, I didn't understand that command.")

if __name__ == '__main__':
    application = ApplicationBuilder().token('6823760649:AAGPR6MCvHEv-QRimKjrz3K_DBSt5EpLqi0').build()
    
    start_handler = CommandHandler('start', start)
    message_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), message)
    video_handler = MessageHandler(filters.VIDEO, video)
    unknown_handler = MessageHandler(filters.COMMAND, unknown)
    
    application.add_handler(start_handler)
    application.add_handler(message_handler)
    application.add_handler(video_handler)
    application.add_handler(unknown_handler)

    application.run_polling()