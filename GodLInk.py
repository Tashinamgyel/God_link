#7910349732:AAGsHmE8zsZ3a4ogqQQpUB5KjNvwJf4en1I
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import yt_dlp
import logging


TOKEN = '7910349732:AAGsHmE8zsZ3a4ogqQQpUB5KjNvwJf4en1I'

# Set up logging for better error handling and debugging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

# Function to handle the /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('Hi! Send me a video link, and I will download it for you.')

# Function to download and send video
async def download_video(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    url = update.message.text
    await update.message.reply_text('Downloading video...')

    video_path = os.path.join(os.getcwd(), 'downloaded_video.mp4')

    try:
        # yt-dlp options to download video, with increased timeout
        ydl_opts = {
            'format': 'best',
            'outtmpl': video_path,
            'socket_timeout': 200,  # Set socket timeout to 60 seconds
        }

        # Try downloading the video
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                ydl.download([url])
            except Exception as download_error:
                await update.message.reply_text(f'Error downloading video: {download_error}')
                logger.error(f"Download error: {download_error}")
                return

        # Check if the file exists after download
        if not os.path.exists(video_path):
            await update.message.reply_text('Failed to download video. The file could not be saved.')
            return

        # Check the file size
        file_size = os.path.getsize(video_path)
        max_size = 50 * 1024 * 1024  # 50 MB for non-premium users

        if file_size > max_size:
            await update.message.reply_text("The downloaded video is too large to send on Telegram.")
        else:
            # Send video if it's within Telegram's size limit
            with open(video_path, 'rb') as video_file:
                await update.message.reply_video(video=video_file)

            # Ensure the video is closed before deleting
            try:
                # Delete the downloaded video file after sending
                os.remove(video_path)
                logger.info(f"Deleted video file: {video_path}")
            except Exception as e:
                # Handle errors in deleting the file
                logger.error(f"Failed to delete video file: {e}")
                await update.message.reply_text("Failed to delete the video file after sending.")
            else:
                logger.info(f"Video file deleted successfully: {video_path}")

    except Exception as e:
        await update.message.reply_text(f'An unexpected error occurred: {str(e)}')
        logger.error(f"Unexpected error: {e}")

# Main function to run the bot
def main() -> None:
    # Initialize the bot application
    application = Application.builder().token(TOKEN).build()

    # Command handler for /start
    application.add_handler(CommandHandler('start', start))

    # Message handler for any text message (link)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_video))

    # Start the bot
    application.run_polling()

if __name__ == '__main__':
    main()




