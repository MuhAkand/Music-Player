from tkinter import *
from tkinter import filedialog, ttk
from pygame import mixer
import os
from PIL import Image, ImageTk
import eyed3
import sv_ttk
import time

mixer.init()

# App Initialization
app = Tk()
app.title('Music Player')
app.geometry('485x700')
app.resizable(False, False)
app.iconbitmap('icon.ico')
sv_ttk.set_theme('dark')

musicFrame = ttk.Frame(app, relief=RIDGE)
musicFrame.place(x=0, y=530, width=485, height=170)

lowerFrame = ttk.Frame(app, width=485, height=100)
lowerFrame.place(x=0, y=400)

# Global Variables
currentSong = None
progressBar = None
totalLength = None
currentTime = None
paused = False


# Play Music
def playMusic():
    global paused
    global currentSong
    if paused:
        mixer.music.unpause()
        paused = False
    else:
        musicName = playlist.get(ACTIVE)
        currentSong = musicName
        mixer.music.load(musicName)
        mixer.music.play()

        # Get the total length of the song
        audio = eyed3.load(musicName)
        global totalLength
        totalLength = audio.info.time_secs

        # Update the progress bar
        updateProgressBar()


# Update the progress bar
def updateProgressBar():
    global progressBar
    global totalLength
    global currentTime

    if totalLength is not None:
        elapsedTime = mixer.music.get_pos() / 1000  # Convert milliseconds to seconds
        currentTime = elapsedTime
        progressPercent = (elapsedTime / totalLength) * 100
        progressBar['value'] = progressPercent
        remainingTime = totalLength - elapsedTime
        mins, secs = divmod(remainingTime, 60)
        progressBar.after(1000, updateProgressBar)  # Update every second
        timeLabel.config(text=f"Time Left: {int(mins)}:{int(secs):02d}")


# Pause Music
def pauseMusic():
    global paused
    mixer.music.pause()
    paused = True


# Browse files for music
def addMusic():
    path = filedialog.askdirectory()
    if path:
        os.chdir(path)
        songs = os.listdir(path)

        playlist.delete(0, END)

        for song in songs:
            if song.endswith('.mp3'):
                playlist.insert(END, song)

                # Display album art if available
                albumArt = getAlbumArt(song)
                if albumArt:
                    image = Image.open(albumArt)
                    image.thumbnail((485, 377))  # Resize the image to fit label dimensions
                    photo = ImageTk.PhotoImage(image)
                    # Ensure photo reference is kept
                    label = ttk.Label(image=photo)
                    label.image = photo  # Keep reference to the image
                    label.place(x=55, y=0, width=485, height=400)  # Adjust placement as necessary
                    app.update()  # Update the GUI to reflect changes


# Get album art from MP3 file
def getAlbumArt(filename):
    audiofile = eyed3.load(filename)
    if audiofile.tag and audiofile.tag.images:
        image_data = audiofile.tag.images[0].image_data
        image_extension = audiofile.tag.images[0].mime_type.split('/')[-1]
        albumArtPath = f"{filename[:-4]}.{image_extension}"
        with open(albumArtPath, "wb") as img_file:
            img_file.write(image_data)
        return albumArtPath
    return None


# Buttons
playButton = ttk.Button(app, text='Play', width=12, command=playMusic)
playButton.place(x=120, y=455)
ttk.Button(app, text='Pause', width=12, command=pauseMusic).place(x=255, y=455)

# Time Labels
timeLabel = Label(app, text="")
timeLabel.place(x=210, y=410)

# Progress bar
progressBar = ttk.Progressbar(lowerFrame, orient=HORIZONTAL, length=430, mode='determinate')
progressBar.place(x=27, y=0)

# Button and Music Box
ttk.Button(app, text='Browse Music', width=58, command=addMusic).place(x=0, y=499)
scroll = Scrollbar(musicFrame)
playlist = Listbox(musicFrame, width=100, bg="#333333", fg="grey", selectbackground="lightblue", cursor="hand2", bd=0,
                   yscrollcommand=scroll.set)
scroll.config(command=playlist.yview)
scroll.pack(side=RIGHT, fill=Y)
playlist.pack(side=RIGHT, fill=BOTH)

app.mainloop()
