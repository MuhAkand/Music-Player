import os
import threading
import time
from tkinter import *
from tkinter import filedialog, ttk

import eyed3
import sv_ttk
from PIL import Image, ImageTk
from pygame import mixer

# Initialize the mixer
mixer.init()


class MusicPlayerApp:
    def __init__(self, root):
        # Initialize the Tkinter root window
        self.root = root
        self.root.title('Music Player')
        self.root.geometry('485x700')
        self.root.resizable(False, False)
        self.root.iconbitmap('icon.ico')
        sv_ttk.set_theme('dark')
        # Initialize instance variables
        self.currentSong = None
        self.paused = False
        self.update_id = None  # Store the ID for progress bar update

        # Setup UI
        self.setupUI()

        # Start the audio playback thread
        self.audio_thread = threading.Thread(target=self.playAudio)
        self.audio_thread.daemon = True  # Daemonize the thread
        self.audio_thread.start()

    def playAudio(self):
        while True:
            if self.currentSong and mixer.music.get_busy() and not self.paused:
                # No need to update UI directly here
                time.sleep(0.1)  # Adjust as needed for smoother playback
            else:
                # If no song is playing, wait for a short duration
                time.sleep(0.1)

    def setupUI(self):
        # Create the music frame
        self.musicFrame = ttk.Frame(self.root, relief=RIDGE)
        self.musicFrame.place(x=0, y=530, width=485, height=170)

        # Create the lower frame
        self.lowerFrame = ttk.Frame(self.root, width=485, height=100)
        self.lowerFrame.place(x=0, y=400)

        # Create buttons
        ttk.Button(self.root, text='Play', width=12, command=self.playMusic).place(x=120, y=455)
        ttk.Button(self.root, text='Pause', width=12, command=self.pauseMusic).place(x=255, y=455)

        # Create time label
        self.timeLabel = Label(self.root, text='')
        self.timeLabel.place(x=210, y=410)

        # Create progress bar
        self.progressBar = ttk.Progressbar(self.lowerFrame, orient=HORIZONTAL, length=430, mode='determinate')
        self.progressBar.place(x=27, y=0)

        # Create browse music button and playlist
        ttk.Button(self.root, text='Browse Music', width=58, command=self.addMusic).place(x=0, y=499)
        self.scroll = Scrollbar(self.musicFrame)
        self.playlist = Listbox(self.musicFrame, width=100, bg='#333333', fg='grey', selectbackground='lightblue',
                                cursor='hand2', bd=0, yscrollcommand=self.scroll.set)
        self.scroll.config(command=self.playlist.yview)
        self.scroll.pack(side=RIGHT, fill=Y)
        self.playlist.pack(side=RIGHT, fill=BOTH)

    def updateUI(self):
        while True:
            if self.currentSong and mixer.music.get_busy() and not self.paused:
                elapsedTime = mixer.music.get_pos() / 1000  # Current playback position in seconds
                audio = eyed3.load(self.currentSong)
                totalLength = audio.info.time_secs
                progressPercent = (elapsedTime / totalLength) * 100

                # Update UI elements (progress bar, timestamp, etc.)
                self.progressBar['value'] = progressPercent
                remainingTime = totalLength - elapsedTime
                mins, secs = divmod(remainingTime, 60)
                if mins and secs != '0':
                    self.timeLabel.config(text=f'Time Left: {int(mins)}:{int(secs):02d}')

            time.sleep(0.1)  # Adjust as needed for smoother UI updates

    def playMusic(self):
        # Play the selected music
        if self.paused:
            mixer.music.unpause()
            self.paused = False
            self.updateProgressBar()  # Resume updating the progress bar
        else:
            musicName = self.playlist.get(ACTIVE)
            self.currentSong = musicName
            mixer.music.load(musicName)
            mixer.music.play()

            # Cancel any scheduled updates from the previous song
            if self.update_id:
                self.root.after_cancel(self.update_id)

            # Display album art for the new song
            self.displayAlbumArt(musicName)

            audio = eyed3.load(musicName)
            totalLength = audio.info.time_secs
            self.updateProgressBar(totalLength)  # Start updating the progress bar for the new song

    def pauseMusic(self):
        # Pause the music
        mixer.music.pause()
        self.paused = True

        # Cancel any scheduled updates from the previous song
        if self.update_id:
            self.root.after_cancel(self.update_id)

    def updateProgressBar(self, totalLength=None):
        # Update the progress bar
        if totalLength is None:
            audio = eyed3.load(self.currentSong)
            totalLength = audio.info.time_secs

        if mixer.music.get_busy() and not self.paused:
            elapsedTime = mixer.music.get_pos() / 1000
            progressPercent = (elapsedTime / totalLength) * 100
            self.progressBar['value'] = progressPercent
            remainingTime = totalLength - elapsedTime
            mins, secs = divmod(remainingTime, 60)
            self.timeLabel.config(text=f'Time Left: {int(mins)}:{int(secs):02d}')
            self.update_id = self.root.after(1000, lambda: self.updateProgressBar(
                totalLength))  # Schedule next update after 1 second
        else:
            # Reset progress bar and time label
            self.progressBar['value'] = 0
            self.timeLabel.config(text='Time Left: 0:00')

    def addMusic(self):
        # Stop the currently playing song, if any
        if mixer.music.get_busy():
            mixer.music.stop()

        # Browse for music files and add them to the playlist
        path = filedialog.askdirectory()
        if path:
            os.chdir(path)
            songs = os.listdir(path)

            self.playlist.delete(0, END)

            for song in songs:
                if song.endswith('.mp3'):
                    self.playlist.insert(END, song)
                    self.displayAlbumArt(song)

    @staticmethod
    def displayAlbumArt(filename):
        # Display album art if available, or a blank white square if not available
        audiofile = eyed3.load(filename)
        if audiofile.tag and audiofile.tag.images:
            # Album art available, display it
            imageData = audiofile.tag.images[0].image_data
            imageExtension = audiofile.tag.images[0].mime_type.split('/')[-1]
            albumArtPath = f'{filename[:-4]}.{imageExtension}'
            with open(albumArtPath, 'wb') as imgFile:
                imgFile.write(imageData)

            image = Image.open(albumArtPath)
            image.thumbnail((485, 377))
        else:
            # No album art available, create a blank white square image
            image = Image.new('RGB', (380, 377), color='white')

        # Display the image
        photo = ImageTk.PhotoImage(image)
        label = ttk.Label(image=photo)
        label.image = photo
        label.place(x=55, y=0, width=485, height=400)

    def __del__(self):
        # Clean up resources when the application is closed
        mixer.quit()


if __name__ == '__main__':
    app = Tk()
    MusicPlayerApp(app)
    app.mainloop()
