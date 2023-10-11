import tkinter as tk
import customtkinter
import csv
import cv2
from PIL import Image, ImageTk
import mediapipe as mp
from GestureRecognizer.recognizer import GestureRecognizer


# ----------- DEFINE INTERFACE ----------- 

customtkinter.set_appearance_mode("Dark")  # Modes: "System" (standard), "Dark", "Light"
customtkinter.set_default_color_theme("green")  # Themes: "blue" (standard), "green", "dark-blue"

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        # Words for prediction
        self.words = []
        # Configure window
        self.title("TalkyHand")

        # Get screen width and height
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        # Calculate the x and y coordinates to center the window
        x = (screen_width - 1200) // 2
        y = (screen_height - 800) // 2

        # Display window in th
        self.geometry(f"1200x800+{x}+{y}")

        # Configure grid layout
        self.grid_columnconfigure(0, weight=0)  # Change weight to 0 to prevent the sidebar from expanding
        self.grid_columnconfigure(1, weight=1)  # Grid for the main container
        self.grid_rowconfigure(0, weight=0) 
        self.grid_rowconfigure(1, weight=1) 

# ----------- CONTAINTER -----------  -> TO CHECK: whether to leave it or just structure more the grid withoud using a container

        self.container = customtkinter.CTkFrame(self, fg_color="#4287f5")
        self.container.grid(row=1, column=1, padx=20, pady=20, sticky="nsew")
        self.container.grid_rowconfigure(0, weight=1)  
        self.container.grid_columnconfigure(0, weight=1) 
        self.container.grid_columnconfigure(1, weight=1)   
  
        # SIDEBAR - navigation
        self.sidebar_frame = customtkinter.CTkFrame(self, width=250, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, rowspan=2, sticky="nsew")
        self.logo_label = customtkinter.CTkLabel(self.sidebar_frame, text="TalkyHand", font=customtkinter.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        # HEADER 
        self.header = customtkinter.CTkLabel(self, text="TalkyHand - your ASL translator Companion", font=customtkinter.CTkFont(size=24, weight="bold"))
        self.header.grid(row=0, column=1, padx=20, pady=(20, 10), sticky="nw")

# ----------- CHAT -----------  -> to do: fix the resize / the right message position / the scrolling

        self.chatFrame = customtkinter.CTkFrame(self.container)
        self.chatFrame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        self.chatFrame.grid_rowconfigure(0, weight=1)  # Allow row 0 (for the chat content) to expand
        self.chatFrame.grid_columnconfigure(0, weight=1)  # Allow column 0 to expand

        self.chat = customtkinter.CTkScrollableFrame(self.chatFrame, label_text="Messages")
        self.chat.grid(row=0, sticky="nsew")

        def gesturer_bt():
            label_gesturer = customtkinter.CTkLabel(self.chat, wraplength=250, fg_color="#63359c", corner_radius=20, text="Gesture to text -> goes here")
            label_gesturer.grid(row=len(self.chat.grid_slaves()) + 1, column=1, padx=10, pady=10, sticky="nsew")
            self.chat.update()

        def speaker_bt():
            label_speaker = customtkinter.CTkLabel(self.chat, wraplength=250, fg_color="#35999c", corner_radius=20, text="Speech to text is going here -> goes here")
            label_speaker.grid(row=len(self.chat.grid_slaves()) + 1, column=2, padx=10, pady=10, sticky="nsew")
            self.chat.update()

        # Remember to edit the buttons 
        button1 = customtkinter.CTkButton(self.chatFrame, text="CTkButton", command=gesturer_bt)
        button2 = customtkinter.CTkButton(self.chatFrame, text="CTkButton", command=speaker_bt)
        button1.grid(row=2, column=0, padx=20, pady=10)
        button2.grid(row=3, column=0, padx=20, pady=10)

        self.entry = customtkinter.CTkEntry(self.chatFrame, placeholder_text="Text here")
        self.entry.grid(row=1, sticky="nsew")

        # create scrollable frame
        # self.scrollable_frame = customtkinter.CTkScrollableFrame(self, corner_radius=30)
        # self.scrollable_frame.grid(row=0, column=2, padx=20, pady=20, sticky="nsew")
        
# ----------- CAMERA ----------- 

        self.camera_canvas = tk.Canvas(self.container, width=600, height=600, bd=0, highlightthickness=0)
        self.camera_canvas.grid(row=0, column=0, padx=(20, 0), pady=20)

        # Start capturing and displaying the camera feed
        self.start_camera()

# ----------- Action for the gesture recognition on the camera -----------

   # Start capturing and displaying the camera feed

    def start_camera(self):
        cap = cv2.VideoCapture(0)

        try:
            gesture_recognizer = GestureRecognizer()
        except Exception as e:
            print(f"Failed to initialize gesture recognizer: {e}")
            return

        mp_drawing = mp.solutions.drawing_utils
        mp_hands = mp.solutions.hands
        hands = mp_hands.Hands(
                static_image_mode=False,
                max_num_hands=2,
            )

        def update_camera():
            _, frame = cap.read()
            if frame is not None:
                # Avoid mirroring the camera feed
                frame_rgb = cv2.cvtColor(cv2.flip(frame, 1), cv2.COLOR_BGR2RGB)

                # Process the frame
                results = hands.process(frame_rgb)
                gesture_recognizer.recognize(frame_rgb)

                # Draw text on the frame
                cv2.putText(frame_rgb, f'Current word: {gesture_recognizer.get_current_text()}', (80, 450), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                self.predictCompletion(gesture_recognizer.get_current_text()[:-1], frame_rgb)

                if results.multi_hand_landmarks:
                    for hand_landmarks in results.multi_hand_landmarks:
                        mp_drawing.draw_landmarks(frame_rgb, hand_landmarks, mp_hands.HAND_CONNECTIONS)

                        # Draw the current gesture on the frame
                    cv2.putText(frame_rgb, f'Recognized: {gesture_recognizer.get_current_gesture()}', (80, 400), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                else:
                    # Draw text on the frame
                    cv2.putText(frame_rgb, f'Recognized: None', (80, 400), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

                # Calculate dimensions to fit the frame within the square canvas
                canvas_size = self.camera_canvas.winfo_width()
                frame_height, frame_width, _ = frame_rgb.shape
                scale_factor = max(canvas_size / frame_width, canvas_size / frame_height)

                # Resize the frame to fill the square canvas
                frame_resized = cv2.resize(frame_rgb, (int(frame_width * scale_factor), int(frame_height * scale_factor)))

                frame_pil = Image.fromarray(frame_resized)
                frame_tk = ImageTk.PhotoImage(image=frame_pil)

                # Clear previous frame and draw the new frame on the canvas
                self.camera_canvas.delete("all")
                self.camera_canvas.create_image(canvas_size // 2, canvas_size // 2, anchor="center", image=frame_tk)
                self.camera_canvas.image = frame_tk

                # Draw rectangles on the camera feed
                self.camera_canvas.create_rectangle(-10, 50, 120, 100, fill="green")  # Top left
                self.camera_canvas.create_rectangle(canvas_size // 2 - 50, 50, canvas_size // 2 + 50, 100, fill="green")  # Top center
                self.camera_canvas.create_rectangle(canvas_size - 120, 50, canvas_size - 50, 100, fill="green")  # Top right
                text_x = (canvas_size - 120 + canvas_size - 50) / 2
                text_y = (50 + 100) / 2
                self.camera_canvas.create_text(text_x, text_y, text="Your Text Here", fill="white")
                
            # Schedule the update function to be called after a delay (e.g., 10 ms)
            self.after(10, update_camera)

        # Start the camera update loop
        update_camera()
    
    def predictCompletion(self, substring, frame_rgb):
        if len(substring) > 1:
            suggestions = [
                word
                for word in self.words
                if word[0].lower().startswith(substring.lower()) and word[0].lower() != substring.lower()
            ]

            final_suggestions = suggestions[:3]
            if len(final_suggestions) > 0:
                cv2.putText(frame_rgb, final_suggestions[0][0], (100, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
            if len(final_suggestions) >= 1:
                cv2.putText(frame_rgb, str(final_suggestions[1][0]), (250, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
            if len(final_suggestions) >= 2:
                cv2.putText(frame_rgb, str(final_suggestions[2][0]), (400, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
            
            
# ----------- LOAD APP ----------- 

if __name__ == "__main__":

    app = App()
    #loading file with words for prediction on finishing a word
    file = open('unigram_freq.csv')
    type(file)
    csvreader = csv.reader(file)
    for row in csvreader:
        app.words.append(row)
    
    app.mainloop()
