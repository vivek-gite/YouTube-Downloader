
import tkinter as tk
from tkinter import ttk
from PIL import ImageTk, Image
import PIL
import requests
from io import BytesIO
from tkinter import *
from tkinter.tix import *
from tkinter import filedialog
from tkinter import messagebox
from pytube import *
import pytube
import threading as th
from tkinter.filedialog import *

main = tk.Tk()

folder_path = StringVar()  # folder path
varsw = []  # Resolution list
Audio_Video = IntVar()  # Audio or video check box
# to keep all IntVars for all filenames
intvar_dict = {}
# to keep all Checkbuttons for all filenames
checkbutton_list = []
# FileSize of the Video
file_size = 0

# main window size
sizex = 1000
sizey = 650
posx = 25
posy = 10
main.geometry("%dx%d" % (sizex, sizey))
main.resizable(0, 0)
main.title("YouTube Downloader")
#youtube_icon=PhotoImage(file="youtube.ico")
main.iconbitmap('.asset\\ytd.ico')


#Menu Bar

menu_bar=Menu(main)
main.config(menu=menu_bar)


# Exit GUI cleanly
def _quit():
    main.quit()
    main.destroy()
    exit()

#Instructions Message box
def _msgBox():
    messagebox.showwarning('Instructions','1.Copy URL from the YouTube and paste it in the Enter URL entry box\n\n'
                                          '2.Click on Browse button to select the path for saving your downloaded video\n\n'
                                          '3.As per your requirement select Audio or Video\n\n'
                                           '4.Click on the Download button')

# Add menu items
file_menu = Menu(menu_bar, tearoff=0)
#file_menu.add_command(label="Instructions",command=_msgBox)
#file_menu.add_separator()
#file_menu.add_command(label="Exit",command=_quit)
#menu_bar.add_cascade(label="Help", menu=file_menu)
menu_bar.add_cascade(label="Instructions",command=_msgBox)
menu_bar.add_cascade(label="Exit",command=_quit)



# ===================================================================
# This is Tooltip i.e if we hover our cursor on that window then this will show us text
class ToolTip(object):
    def __init__(self, widget):
        self.widget = widget
        self.tip_window = None

    def show_tip(self, tip_text):
        "Display text in a tooltip window"
        if self.tip_window or not tip_text:
            return
        x, y, _cx, cy = self.widget.bbox("insert")  # get size of widget
        x = x + self.widget.winfo_rootx() + 25  # calculate to display tooltip
        y = y + cy + self.widget.winfo_rooty() + 10  # below and to the right
        self.tip_window = tw = tk.Toplevel(self.widget)  # create new tooltip window
        tw.wm_overrideredirect(True)  # remove all Window Manager (wm) decorations
        #         tw.wm_overrideredirect(False)                 # uncomment to see the effect
        tw.wm_geometry("+%d+%d" % (x, y))  # create window size

        label = tk.Label(tw, text=tip_text, justify=tk.LEFT,
                         background="#e6e6e6", relief=tk.SOLID, borderwidth=1,
                         font=("tahoma", "8", "normal"))
        label.pack(ipadx=1)

    def hide_tip(self):
        tw = self.tip_window
        self.tip_window = None
        if tw:
            tw.destroy()


def create_ToolTip(widget, text):
    toolTip = ToolTip(widget)  # create instance of class

    def enter(event):
        toolTip.show_tip(text)

    def leave(event):
        toolTip.hide_tip()

    widget.bind('<Enter>', enter)  # bind mouse events
    widget.bind('<Leave>', leave)


# ====================================================================================


# =====================================================================================
# This the Context Menu i.e if we right click on the entry box then it must show us cut,copy,paste
def rClicker(e):
    ''' right click context menu for all Tk Entry and Text widgets
    '''

    try:
        def rClick_Copy(e, apnd=0):
            e.widget.event_generate('<Control-c>')

        def rClick_Cut(e):
            e.widget.event_generate('<Control-x>')

        def rClick_Paste(e):
            e.widget.event_generate('<Control-v>')

        e.widget.focus()

        nclst = [
            (' Cut', lambda e=e: rClick_Cut(e)),
            (' Copy', lambda e=e: rClick_Copy(e)),
            (' Paste', lambda e=e: rClick_Paste(e)),
        ]

        rmenu = Menu(None, tearoff=0, takefocus=0)

        for (txt, cmd) in nclst:
            rmenu.add_command(label=txt, command=cmd)

        rmenu.tk_popup(e.x_root + 40, e.y_root + 10, entry="0")

    except TclError:
        print(' - rClick menu, something wrong')
        pass

    return "break"


def rClickbinder(r):
    try:
        for b in ['Text', 'Entry', 'Listbox', 'Label']:  #
            r.bind_class(b, sequence='<Button-3>',
                         func=rClicker, add='')
    except TclError:
        print(' - rClickbinder, something wrong')
        pass


# ===============================================================================================


def resolution_list():
    global Audio_Video
    global url_str

    try:

        ob = YouTube(url_str.get())
        text = []
        itag_list = []

        if (Audio_Video.get() == 1):

            stri = ob.streams.filter(type="video")
            for i in stri:
                if i.resolution is None:
                    continue
                k = f'Res:{i.resolution}, FPS:{i.fps}, Video codec:{i.video_codec}, Audio codec:{i.audio_codec},' \
                    f' File type:{i.mime_type.split("/")[1]}, Size:{str(round(i.filesize / (1024 * 1024)))} MB'

                text.append(k)
                itag_list.append(i.itag)

        elif (Audio_Video.get() == 2):
            stri = ob.streams.filter(type="audio")
            itag_list = []
            text = []
            for i in stri:
                k = f'Codec: {i.audio_codec}, ABR: {i.abr}, File type: {i.mime_type.split("/")[1]}, ' \
                    f'Size: {str(round(i.filesize / (1024 * 1024)))} MB'

                text.append(k)
                itag_list.append(i.itag)
        return [text, itag_list]
    except Exception as e:
        messagebox.showinfo("Media error",
                            f'Reasons for this error:\n'
                            f' 1.The Input URL is incorrect.\n 2.The Video is Age Restricted\n '
                            f'3.The video is restricted for using in any 3rd party application.')
        confirm['text'] = "Confirm"
        confirm.config(state=NORMAL)


def confirm_Button():
    global intvar_dict
    intvar_dict.clear()  # Variable dictionary for resolution list
    text_check, itag_check = resolution_list()

    for cb in checkbutton_list:
        cb.destroy()
    checkbutton_list.clear()

    content = tk.Frame(hel_frame, relief='groove', bd=2)
    canvas = tk.Canvas(content, borderwidth=0, height=395, width=578)
    myscrollbar = Scrollbar(content, orient="vertical", command=canvas.yview)
    frame = ttk.Frame(canvas)
    canvas.configure(yscrollcommand=myscrollbar.set)
    content.grid_configure(row=5, column=0, rowspan=1, sticky='NSEW')
    myscrollbar.pack(side="right", fill="y")
    canvas.pack(side='left')
    canvas.create_window((0, 0), window=frame, anchor="nw", tags="frame")
    confirm['text'] = "Fetching..."
    confirm.config(state=DISABLED)
    frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    confirm['text'] = "Confirm"
    confirm.config(state=NORMAL)

    # Add scroll (Incomplete)
    i = 0
    for resname in text_check:
        intvar_dict[resname] = tk.IntVar()
        # create Checkbutton for filename and keep on list
        cb = tk.Checkbutton(frame, text=resname, variable=intvar_dict[resname], onvalue=itag_check[i], offvalue=0,
                            command=lambda: test_v())
        i += 1
        cb.grid(row=i, column=0, sticky="")
        checkbutton_list.append(cb)


def check_video():
    global Audio_Video
    if len(path.get()) == 0:
        messagebox.showinfo("URL Info", "Enter the URL First")
        confirm['text'] = "Confirm"
        confirm.config(state=NORMAL)

    elif (Audio_Video.get() == 0):
        messagebox.showinfo("Box Selection", "Check the Audio or Video Box")
    elif (Audio_Video.get() != 0) and len(path.get()) > 0:
        confirm['text'] = "Fetching..."
        confirm.config(state=DISABLED)
        confirm_Button()
        #th.Thread(target=confirm_Button).start()


def test_v():
    """url = YouTube(str(path.get()))
    url_link = str(url.thumbnail_url)
    res = requests.get(url_link)
    img_d = res.content
    img = ImageTk.PhotoImage(PIL.Image.open(BytesIO(img_d)))
    to = Label(btn_Frame, image=img,height=100,width=80)
    to.place(x=650, y=200,anchor = CENTER)
"""
    global intvar_dict
    c = 0
    ret = None
    val = list(intvar_dict.values())
    val1 = [i.get() for i in val]

    ind = 0
    for key, value in intvar_dict.items():
        if value.get() > 0:
            ret = value.get()
            ind = val1.index(ret)
            c = 1
    if (c == 0):
        for i in range(len(intvar_dict)):
            checkbutton_list[i].config(state='normal')
    elif (c == 1):
        for i in range(len(intvar_dict)):
            if (i == ind):
                continue
            checkbutton_list[i].config(state='disabled')
    return ret


def browse_button():
    global folder_path
    global filename
    filename = filedialog.askdirectory(title='Choose a file')
    folder_path.set(filename)


def progressDownlaod(stream=None, chunk=None, bytes_remaining=None):
    percentage = ((file_size - bytes_remaining) / (file_size)) * 100
    main.update_idletasks()
    progress_bar['value'] = percentage


def Download():
    ita_ret = test_v()
    if len(path.get())==0:
        messagebox.showinfo("URL Info", "Enter the URL")
    elif len(folder_path.get()) == 0:
        messagebox.showinfo("Empty Path", "Select Path")
    elif ita_ret is None:
        messagebox.showinfo("Media","Select the media")
    global file_size

    my_video = YouTube(path.get())
    stre = my_video.streams.get_by_itag(ita_ret)
    my_video.register_on_progress_callback(progressDownlaod)
    file_size = stre.filesize
    if len(filename)!=0:
        download_button['text']="Downloading..."
        download_button.config(state=DISABLED)
        stre.download(filename)
        download_button['text'] = "Download"
        download_button.config(state=NORMAL)
        messagebox.showinfo('Complete', "Video is Downloaded check your file location")
    

back=PhotoImage(file=".asset\\fixed2.png")

btn_Frame = Frame(main)
btn_Frame.place(relheight=1, relwidth=1)

back_ground=Label(btn_Frame,image=back)
back_ground.place(relheight=1, relwidth=1)

#header_label = tk.Label(btn_Frame, height=1, width=80)
#header_label.grid(row=1, column=1, padx=10, pady=10, columnspan=5)

# Enter URL Label

url_img=PhotoImage(file=".asset\\url.png")
lbl_url = tk.Label(btn_Frame, image=url_img, width=15, height=1, fg="red", bg="#ccf2ff",
                   font=('League Spartan', 10, ' bold '))
lbl_url.grid(row=2, column=0, padx=30, pady=20,ipadx=33,ipady=15)

# Enter path label
file_img=PhotoImage(file=".asset\\path.png")
lbl_path = tk.Label(btn_Frame,image=file_img, text="Enter path", width=13, height=1, fg="red", bg="#ccf2ff",
                    font=('League Spartan', 10, ' bold '))
lbl_path.grid(row=3, column=0, padx=30,ipadx=36,ipady=15)

# Url Entry
url_str = StringVar()
path = ttk.Entry(btn_Frame, width=60, textvariable=url_str, font=('DM Sans', 10))
path.grid(row=2, column=1, ipady=2, padx=0, pady=5, sticky="W", columnspan=2)
# Context Menu(i.e, cut,copy,paste on right click)
path.bind('<Button-3>', rClicker, add='')

# Add a Tooltip
create_ToolTip(path, 'Press CTRL+V to Paste')

# path Entry
file = ttk.Entry(btn_Frame, width=60, textvariable=folder_path, font=('DM Sans', 10))
file.grid(row=3, column=1, ipady=2, padx=0, pady=5, columnspan=2)
# Context Menu(i.e, cut,copy,paste on right click)
file.bind('<Button-3>', rClicker, add='')

# video checkbox
video_icon=PhotoImage(file=".asset\\video1.png")
video_check = tk.Checkbutton(btn_Frame,image=video_icon, text="video", onvalue=1, variable=Audio_Video,bg="#f85646",relief="solid")
video_check.grid(row=4, column=1, padx=0)

# audio checkbox
audio_icon=PhotoImage(file=".asset\\audio1.png")
audio_check = tk.Checkbutton(btn_Frame,image=audio_icon, text="Audio", onvalue=2, variable=Audio_Video,bg="#f85646", relief="solid")
audio_check.grid(row=4, column=2, padx=0)

# confirm Button

confirm_img=PhotoImage(file=".asset\\checkvideo.png")
confirm = tk.Button(btn_Frame, image=confirm_img,text="Check video",width=85,height=29,bd=0, command=lambda: check_video())
confirm.grid(row=2, column=3, padx=10, pady=5)

# browse Button
imf=PhotoImage(file=".asset\\Browse2.png")
browse = Button(btn_Frame, image=imf,text="Browse", width=85,height=29, command=lambda: browse_button(),bd=0)
browse.grid(row=3, column=3, padx=6, pady=5)

hel_frame = ttk.Frame(btn_Frame, relief='groove', height=400, width=600)
hel_frame.grid(row=5, column=0, padx=20, pady=20, rowspan=1, columnspan=4)

# Download Progress
download_prog=PhotoImage(file=".asset\\downloadprogr1.png")
download_Frame = tk.Label(btn_Frame,image=download_prog, height=80, width=290,bg="#f85646").place(x=665, y=255)
#tk.Label(btn_Frame,image=download_prog,text="Download Progress :", font=('verdana', 15)).place(x=630, y=270)
progress_bar = ttk.Progressbar(btn_Frame, orient='horizontal', length=230, mode='determinate')
progress_bar.place(x=698, y=300, relheight=0.04)

progress_bar['value'] = 0
progress_bar['maximum'] = 100


# Download Button
#s = ttk.Style()
#s.configure('my.TButton', font=('verdana', 20))
ty=PhotoImage(file=".asset\\downloadicon1.png")

download_button = tk.Button(main,text="Download",image=ty,bg="#f85646",height=73, width=207, command=lambda: th.Thread(target=Download).start(),bd=0)
download_button.place(x=680, y=380)

main.mainloop()


