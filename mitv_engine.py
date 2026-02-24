import time
import subprocess
import os
import firebase_admin
from firebase_admin import credentials, db
from colorama import Fore, Style, init

init(autoreset=True)

class MiTVCloudEngine:
    def __init__(self):
        self.process = None
        self.current_link = ""
        self.current_key = ""
        self.current_bitrate = "2000k" # Default bitrate

        print(f"{Fore.CYAN} MiTV CLOUD ENGINE STARTING...")

        # Firebase Setup
        try:
            # GitHub Secrets se key uthana ya direct file use karna
            cred = credentials.Certificate("key.json")
            firebase_admin.initialize_app(cred, {
                'databaseURL': 'https://ramadan-2385b-default-rtdb.firebaseio.com'
            })
            self.db_ref = db.reference('/')
            print(f"{Fore.GREEN}[+] Firebase Connected!")
        except Exception as e:
            print(f"{Fore.RED}[-] Error: {e}")
            exit()

    def start_stream(self, link, stream_key, bitrate):
        if self.process:
            self.process.terminate()
        
        youtube_url = f"rtmp://a.rtmp.youtube.com/live2/{stream_key}"
        
        # Cloud optimized FFmpeg
        ffmpeg_cmd = [
            'ffmpeg', '-re', 
            '-user_agent', 'Mozilla/5.0',
            '-i', link,
            '-c:v', 'libx264', '-preset', 'veryfast', 
            '-b:v', bitrate, '-maxrate', bitrate, '-bufsize', '4000k',
            '-pix_fmt', 'yuv420p', '-g', '60',
            '-c:a', 'aac', '-b:a', '128k', '-f', 'flv',
            youtube_url
        ]

        self.process = subprocess.Popen(ffmpeg_cmd)
        self.current_link = link
        self.current_key = stream_key
        self.current_bitrate = bitrate
        print(f"{Fore.GREEN}[LIVE] Streaming Started!")

    def run(self):
        while True:
            try:
                data = self.db_ref.get()
                if data:
                    new_link = data.get('stream_link', "")
                    new_key = data.get('stream_key', "")
                    new_bitrate = data.get('bitrate', "2000k")

                    if new_link != self.current_link or new_key != self.current_key or new_bitrate != self.current_bitrate:
                        if new_link:
                            self.start_stream(new_link, new_key, new_bitrate)
                        else:
                            if self.process:
                                self.process.terminate()
                                self.current_link = ""
                                print(f"{Fore.RED}[STOPPED] Admin request.")

                time.sleep(10) # 10 seconds check interval
            except Exception as e:
                print(f"Loop Error: {e}")
                time.sleep(10)

if __name__ == "__main__":
    engine = MiTVCloudEngine()
    engine.run()
      
