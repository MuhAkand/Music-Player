from tkinter import *
from tkinter import filedialog
from pygame import mixer
import os
from PIL import Image, ImageTk
import eyed3
mixer.init()

# App Initialization
app = Tk()
app.title('Music Player')
app.geometry('485x700')
app.config(bg='#2A2D34')
app.resizable(False, False)
app.iconbitmap('icon.ico')

musicFrame = Frame(app, bd=2, relief=RIDGE)
musicFrame.place(x=0, y=530, width=485, height=150)

lowerFrame = Frame(app, bg='#30C5FF', width=485, height=100)
lowerFrame.place(x=0, y=400)


# Play Music
def playMusic():
    musicName = Playlist.get(ACTIVE)
    print(musicName)
    mixer.music.load(musicName)
    mixer.music.play()


# Browse files for music
def addMusic():
    path = filedialog.askdirectory()
    if path:
        os.chdir(path)
        songs = os.listdir(path)

        Playlist.delete(0, END)

        for song in songs:
            if song.endswith('.mp3'):
                Playlist.insert(END, song)
                # Display album art if available
                album_art = get_album_art(song)
                if album_art:
                    image = Image.open(album_art)
                    image.thumbnail((485, 400))  # Resize the image to fit label dimensions
                    photo = ImageTk.PhotoImage(image)
                    # Ensure photo reference is kept
                    label = Label(image=photo, bg='#2A2D34')
                    label.image = photo  # Keep reference to the image
                    label.place(x=0, y=0, width=485, height=400)  # Adjust placement as necessary
                    app.update()  # Update the GUI to reflect changes


# Get album art from MP3 file
def get_album_art(filename):
    audiofile = eyed3.load(filename)
    if audiofile.tag and audiofile.tag.images:
        image_data = audiofile.tag.images[0].image_data
        image_extension = audiofile.tag.images[0].mime_type.split('/')[-1]
        album_art_path = f"{filename[:-4]}.{image_extension}"
        with open(album_art_path, "wb") as img_file:
            img_file.write(image_data)
        return album_art_path
    return None


# Buttons
Button(app, text='Play', height=6, width=12, command=playMusic).place(x=200, y=400)
Button(app, text='Unpause', height=6, width=12, command=mixer.music.unpause).place(x=50, y=400)
Button(app, text='Pause', height=6, width=12, command=mixer.music.pause).place(x=340, y=400)


# Button and Music Box
Button(app, text='Browse Music', width=68, height=1, fg='#30C5FF', bg='#2A2D34', command=addMusic).place(x=0, y=500)
Scroll = Scrollbar(musicFrame)
Playlist = Listbox(musicFrame, width=100, bg="#333333", fg="grey", selectbackground="lightblue", cursor="hand2", bd=0,
                   yscrollcommand=Scroll.set)
Scroll.config(command=Playlist.yview)
Scroll.pack(side=RIGHT, fill=Y)
Playlist.pack(side=RIGHT, fill=BOTH)

app.mainloop()
