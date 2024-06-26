import os
import sv_ttk
import threading
import time
from tkinter import *
from tkinter import filedialog, ttk
import eyed3
from PIL import Image, ImageTk
from pygame import mixer

# Initialize mixer
mixer.init()


class MusicPlayerApp:
    def __init__(self, root):
        self.root = root
        self.setup_window()
        self.setup_variables()
        self.setup_ui()
        self.setup_audio_thread()

    def setup_window(self):
        # Set up the main window
        self.root.title('Music Player')
        self.root.geometry('485x700')
        self.root.resizable(False, False)
        self.root.iconbitmap('icon.ico')
        sv_ttk.set_theme('dark')

    def setup_variables(self):
        # Initialize variables
        self.current_song = None
        self.paused = False
        self.update_id = None

    def setup_ui(self):
        # Set up the user interface components
        self.setup_music_frame()
        self.setup_lower_frame()
        self.setup_buttons()
        self.setup_time_label()
        self.setup_progress_bar()
        self.setup_playlist()

    def setup_music_frame(self):
        # Set up frame for displaying album art and song information
        self.music_frame = ttk.Frame(self.root)
        self.music_frame.place(x=0, y=530, width=485, height=170)

    def setup_lower_frame(self):
        # Set up lower frame for control buttons and progress bar
        self.lower_frame = ttk.Frame(self.root, width=485, height=100)
        self.lower_frame.place(x=0, y=400)

    def setup_buttons(self):
        # Set up control buttons
        ttk.Button(self.root, text='Play', width=12, command=self.play_music).place(x=115, y=455)
        ttk.Button(self.root, text='Pause', width=12, command=self.pause_music).place(x=255, y=455)
        ttk.Button(self.root, text='Browse Music', width=58, command=self.add_music).place(x=0, y=499)
        ttk.Button(self.root, text='/', width=1, command=self.change_theme).place(x=10, y=10)
        ttk.Button(self.root, text='+', width=1, command=self.vol_up).place(x=10, y=420)
        ttk.Button(self.root, text='-', width=1, command=self.vol_down).place(x=10, y=455)

    def setup_time_label(self):
        # Label to display remaining time
        self.time_label = Label(self.root, text='')
        self.time_label.place(x=210, y=410)

    def setup_progress_bar(self):
        # Progress bar to indicate playback progress
        self.progress_bar = ttk.Progressbar(self.lower_frame, orient=HORIZONTAL, length=430, mode='determinate')
        self.progress_bar.place(x=27, y=0)

    def setup_playlist(self):
        # Playlist to display available songs
        self.scroll = Scrollbar(self.music_frame)
        self.playlist = Listbox(self.music_frame, width=100, selectbackground='#4287f5',
                                cursor='hand2', bd=0, yscrollcommand=self.scroll.set)
        self.scroll.config(command=self.playlist.yview)
        self.scroll.pack(side=RIGHT, fill=Y)
        self.playlist.pack(side=RIGHT, fill=BOTH)

    def setup_audio_thread(self):
        # Start a thread for handling audio playback
        self.audio_thread = threading.Thread(target=self.play_audio)
        self.audio_thread.daemon = True
        self.audio_thread.start()

    def play_audio(self):
        # Function to continuously check for playback and update progress bar
        while True:
            if self.current_song and mixer.music.get_busy() and not self.paused:
                time.sleep(0.1)
            else:
                time.sleep(0.1)

    def play_music(self):
        # Function to play music
        if self.paused:
            mixer.music.unpause()
            self.paused = False
            self.update_progress_bar()
        else:
            music_name = self.playlist.get(ACTIVE)
            self.current_song = music_name
            mixer.music.load(music_name)
            mixer.music.play()
            if self.update_id:
                self.root.after_cancel(self.update_id)
            self.display_album_art(music_name)
            audio = eyed3.load(music_name)
            total_length = audio.info.time_secs
            self.update_progress_bar(total_length)

    def pause_music(self):
        # Function to pause music
        mixer.music.pause()
        self.paused = True
        if self.update_id:
            self.root.after_cancel(self.update_id)

    def update_progress_bar(self, total_length=None):
        # Function to update progress bar based on playback
        if total_length is None:
            audio = eyed3.load(self.current_song)
            total_length = audio.info.time_secs

        if mixer.music.get_busy() and not self.paused:
            elapsed_time = mixer.music.get_pos() / 1000
            progress_percent = (elapsed_time / total_length) * 100
            self.progress_bar['value'] = progress_percent
            remaining_time = total_length - elapsed_time
            mins, secs = divmod(remaining_time, 60)
            self.time_label.config(text=f'Time Left: {int(mins)}:{int(secs):02d}')
            self.update_id = self.root.after(1000, lambda: self.update_progress_bar(total_length))
        else:
            self.progress_bar['value'] = 0
            self.time_label.config(text='Time Left: 0:00')

    def add_music(self):
        # Function to add music to the playlist
        if mixer.music.get_busy():
            mixer.music.stop()

        path = filedialog.askdirectory()
        if path:
            os.chdir(path)
            songs = os.listdir(path)
            self.playlist.delete(0, END)

            for song in songs:
                if song.endswith('.mp3'):
                    self.playlist.insert(END, song)
                    self.display_album_art(song)

    @staticmethod
    def vol_up():
        mixer.music.set_volume(min(1.0, mixer.music.get_volume() + 0.1))

    @staticmethod
    def vol_down():
        mixer.music.set_volume(max(0.0, mixer.music.get_volume() - 0.1))

    @staticmethod
    def display_album_art(filename):
        # Function to display album art for the current song
        audiofile = eyed3.load(filename)
        if audiofile.tag and audiofile.tag.images:
            image_data = audiofile.tag.images[0].image_data
            image_extension = audiofile.tag.images[0].mime_type.split('/')[-1]
            album_art_path = f'{filename[:-4]}.{image_extension}'
            with open(album_art_path, 'wb') as img_file:
                img_file.write(image_data)
            image = Image.open(album_art_path)
            image.thumbnail((485, 377))
        else:
            image = Image.new('RGB', (380, 377), color='gray')

        photo = ImageTk.PhotoImage(image)
        label = ttk.Label(image=photo)
        label.image = photo
        label.place(x=55, y=0, width=485, height=400)

    @staticmethod
    def change_theme():
        # Function to change the theme between dark and light
        current_theme = sv_ttk.get_theme()
        if current_theme == 'dark':
            sv_ttk.set_theme('light')
        else:
            sv_ttk.set_theme('dark')

    def __del__(self):
        # Cleanup when the instance is destroyed
        mixer.quit()


if __name__ == '__main__':
    app = Tk()
    MusicPlayerApp(app)
    app.mainloop()
