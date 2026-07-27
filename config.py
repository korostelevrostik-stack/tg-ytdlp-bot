# Config
class Config(object):
    # Your bot name - Required (str)
    BOT_NAME = "public"
    # A name for users - Required (str)
    BOT_NAME_FOR_USERS = "Video Downloader bot"
    # Add all admin id's as a list - Required (lst[int])
    ADMIN = [8261666607]
    # Add your telegram API ID - Required (int)
    API_ID = 0
    # Add your Telegram API HASH - Required (str)
    API_HASH = ""
    # Add your telegram bot token (str)
    BOT_TOKEN = "8707409862:AAFEfJxi8sXmCdg1Uy9Nb-R4qBMFSzl83Rw"
    # Add telegram Log channel Id - Required (int)
    LOGS_ID = 8261666607

    # Cookie file URL
    # EX: "https://path/to/your/cookie-file.txt"
    COOKIE_URL = ""
    # Do not chanege this
    COOKIE_FILE_PATH = "cookies.txt"
    # Do not chanege this
    PIC_FILE_PATH = "pic.jpg"

    # Restricted content site lists
    PORN_LIST = ["pornhub", "phncdn.com", "xvideos", "xhcdn.com", "xhamster"]

    # Commands
    DOWNLOAD_COOKIE_COMMAND = "/download_cookie"
    CHECK_COOKIE_COMMAND = "/check_cookie"
    SAVE_AS_COOKIE_COMMAND = "/save_as_cookie"
    AUDIO_COMMAND = "/audio"
    FORMAT_COMMAND = "/format"
    COOKIES_FROM_BROWSER_COMMAND = "/cookies_from_browser"
    BLOCK_USER_COMMAND = "/block_user"
    UNBLOCK_USER_COMMAND = "/unblock_user"
    RUN_TIME = "/run_time"
    GET_USER_LOGS_COMMAND = "/log"
    CLEAN_COMMAND = "/clean"
    USAGE_COMMAND = "/usage"
    BROADCAST_MESSAGE = "/broadcast"
    # this is a main cmd - to user /get_user_details_users
    GET_USER_DETAILS_COMMAND = "/all"

    # Messages and errors
    CREDITS_MSG = ""
    TO_USE_MSG = "__To use this bot you need to subscribe to the channel.__\nAfter you join the channel, **resend your video link again and I will download it for you** ❤️  "
    MSG1 = "Hello "
    MSG2 = "This is the second message. which means my own message... 😁"
    ERROR1 = "Did not found a url link. Please enter a url with **https://** or **http://**"
    INDEX_ERROR = "You did not give a valid information. Try again..."
    HELP_MSG = """
> **This bot allows you to download videos and audio, and also work with playlists.**
> 
> • Simply send a video link and the bot will start downloading.
> • For playlists, specify the range of indexes separated by asterisks (e.g. `https://example.com*1*4`) to download videos from position 1 to 4.
> • You can set a custom playlist name by adding it after the range (e.g. `https://example.com*1*4*My Playlist`).
> 
> • To change the caption of a video, reply to the video with your message – the bot will send the video with your caption.
> • To extract audio from a video, use the **/audio** command (e.g. `/audio https://example.com`).
> • Upload a cookie file to download private videos and playlists.
> • Check or update your cookie file with **/check_cookie**, **/download_cookie**, **/save_as_cookie** and **/cookies_from_browser** commands.
> • To clean your workspace on server from bad files (e.g. old cookies or media) use **/clean** command (might be helpfull for get rid of errors).
> • See your usage statistics and logs by sending the **/usage** command.
"""

    # Firebase Initialization with Authentication
# Проверяем, есть ли Firebase конфиг. Если нет — работаем без него.
if Config.FIREBASE_CONF and Config.FIREBASE_USER and Config.FIREBASE_PASSWORD:
    firebase = pyrebase.initialize_app(Config.FIREBASE_CONF)
    auth = firebase.auth()
    try:
        user = auth.sign_in_with_email_and_password(Config.FIREBASE_USER, Config.FIREBASE_PASSWORD)
        logger.info("User signed in successfully.")
        idToken = user.get("idToken")
        logger.info(f"Firebase idToken (first 20 chars): {idToken[:20]}")
    except Exception as e:
        logger.error(f"Error during Firebase authentication: {e}")
        idToken = None
else:
    logger.info("Firebase credentials not configured — running without Firebase.")
    idToken = None

# Если Firebase подключена — создаём обёртку для базы данных
if idToken:
    base_db = firebase.database()
    class AuthedDB:
        def __init__(self, db, token):
            self.db = db
            self.token = token
        def child(self, path):
            return AuthedDB(self.db.child(path), self.token)
        def set(self, data, *args, **kwargs):
            return self.db.set(data, self.token, *args, **kwargs)
        def get(self, *args, **kwargs):
            return self.db.get(self.token, *args, **kwargs)
        def push(self, data, *args, **kwargs):
            return self.db.push(data, self.token, *args, **kwargs)
        def update(self, data, *args, **kwargs):
            return self.db.update(data, self.token, *args, **kwargs)
        def remove(self, *args, **kwargs):
            return self.db.remove(self.token, *args, **kwargs)
    db = AuthedDB(base_db, idToken)
    db_path = Config.BOT_DB_PATH.rstrip("/")
    _format = {"ID": "0", "timestamp": math.floor(time.time())}
    try:
        result = db.child(f"{db_path}/users/0").set(_format)
        logger.info("Data written successfully. Result:", result)
    except Exception as e:
        logger.error("Error writing data to Firebase:", e)
    def token_refresher():
        global db, user
        while True:
            time.sleep(3000)
            try:
                new_user = auth.refresh(user["refreshToken"])
                new_idToken = new_user["idToken"]
                db.token = new_idToken
                user = new_user
                logger.info("Firebase idToken refreshed successfully.")
            except Exception as e:
                logger.error("Error refreshing Firebase idToken:", e)
    token_thread = threading.Thread(target=token_refresher, daemon=True)
    token_thread.start()
else:
    logger.warning("Firebase disabled. Some admin/stat commands may not work.")
