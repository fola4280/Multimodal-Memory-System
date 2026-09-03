from email.mime import image
import os
import json
import shutil
import tkinter.filedialog as fd
import time
from response_engine import trigger_response
from identity_database import identity_map
from camera import Camera
import cv2
from PIL import Image, ImageTk
import random
from unicodedata import name
from identity_database import identity_map
import customtkinter as ctk
from recognition import load_faces, recognise


ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")


class MemoryBridgeGUI:

    def __init__(self):

        self.root = ctk.CTk()
        self.root.title("MemoryBridge")
        self.root.geometry("1100x750")
        self.root.resizable(False, False)

        self.build_gui()
        
        self.camera = None 
        
        self.face_detected_time = None
        self.person_recognised = False
        
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.root.mainloop()
        
    def add_log(self, message):

        self.log_box.configure(state="normal")

        self.log_box.insert("end", message + "\n")

        self.log_box.see("end")

        self.log_box.configure(state="disabled")
        
    def open_register(self):
        self.register = ctk.CTkToplevel(self.root)
        self.register.title("Register Person")
        self.register.geometry("450x650")
        
        ctk.CTkLabel(
            self.register,
            text="Register New Person",
            font=("Segoe UI", 24, "bold")
        ).pack(pady=20)
        
        self.register_camera = ctk.CTkLabel(
            self.register,
            text="Camera Preview",
            width=250,
            height=220,
            fg_color="#d9d9d9"
        )

        self.register_camera.pack(pady=15)
        
        self.name_entry = ctk.CTkEntry(
            self.register,
            placeholder_text="Name"
        )
        self.name_entry.pack(fill="x", padx=30, pady=10)
        
        self.scent_entry = ctk.CTkEntry(
            self.register,
            placeholder_text="Favourite Scent"
        )
        self.scent_entry.pack(fill="x", padx=30, pady=10)

        self.audio_entry = ctk.CTkEntry(
            self.register,
            placeholder_text="Greeting Audio"
        )
        self.audio_entry.pack(fill="x", padx=30, pady=10)


        ctk.CTkButton(
            self.register,
            text="Capture Face",
            command=self.capture_face
        ).pack(pady=10)

        ctk.CTkButton(
            self.register,
            text="Save Person",
            command=self.save_person
        ).pack(pady=20)
        
    def upload_photo(self):

        self.photo_path = fd.askopenfilename(
            filetypes=[
                ("Images", "*.jpg *.jpeg *.png")
            ]
        )
        
    def capture_face(self):

        if self.camera is None:
            self.camera = Camera()

        frame, faces = self.camera.get_frame()

        if frame is None:
            return
        
        if len(faces) == 0:
            self.status.configure(
                text="Status: No face detected. Please try again."
            )
            return

        self.captured_frame = frame

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        image = Image.fromarray(rgb)
        
        image = image.resize((250,220))

        photo = ctk.CTkImage(
            light_image=image,
            dark_image=image,
            size=(250,220)
        )

        self.register_camera.configure(
            image=photo,
            text=""
        )

        self.register_camera.image = photo
        
        self.status.configure(
            text="Status: Face captured. Please fill in the details and save."
        )
        
    def save_person(self):

        name = self.name_entry.get().strip()

        if name == "":
            return
        
        folder = os.path.join("faces", name)

        os.makedirs(folder, exist_ok=True)

        photo_path = os.path.join(folder, "face.jpg")

        cv2.imwrite(photo_path, self.captured_frame)

        identity_map[name] = {

            "scent": self.scent_entry.get(),

            "audio": self.audio_entry.get(),

            "photo": photo_path

        }

        self.add_log(f"{name} registered.")

        self.register.destroy()
        
        with open("people.json", "w") as file:
            json.dump(identity_map, file, indent=4)
    
    def build_gui(self):

        title = ctk.CTkLabel(
            self.root,
            text="MemoryBridge",
            font=("Segoe UI", 34, "bold")
        )
        title.pack(pady=(20,5))

        subtitle = ctk.CTkLabel(
            self.root,
            text="Multimodal Memory Support Prototype",
            font=("Segoe UI",18)
        )
        subtitle.pack()

        # Main Frame
        main_frame = ctk.CTkFrame(self.root)
        main_frame.pack(fill="both", expand=True, padx=30, pady=25)

        # Left Side
        left = ctk.CTkFrame(main_frame, width=420)
        left.pack(side="left", fill="both", expand=True, padx=15, pady=15)

        camera_title = ctk.CTkLabel(
            left,
            text="Camera Preview",
            font=("Segoe UI",22,"bold")
        )
        camera_title.pack(pady=10)

        self.camera_box = ctk.CTkLabel(
            left,
            text="Camera not started",
            width=360,
            height=320,
            fg_color="#d9d9d9",
            corner_radius=12
        )

        self.camera_box.pack(pady=15)

        self.progress = ctk.CTkProgressBar(left)

        self.progress.pack(pady=10)

        self.progress.set(0)
        
        # Right Side
        right = ctk.CTkFrame(main_frame)
        right.pack(side="right", fill="both", expand=True, padx=15, pady=15)

        info = ctk.CTkLabel(
            right,
            text="Recognition Details",
            font=("Segoe UI",22,"bold")
        )
        info.pack(pady=10)

        self.person = ctk.CTkLabel(
            right,
            text="Person: Waiting...",
            font=("Segoe UI",18)
        )
        self.person.pack(anchor="w", padx=25, pady=10)

        self.relationship = ctk.CTkLabel(
            right,
            text="Relationship: --",
            font=("Segoe UI",18)
        )
        self.relationship.pack(anchor="w", padx=25, pady=10)

        self.scent = ctk.CTkLabel(
            right,
            text="Scent: --",
            font=("Segoe UI",18)
        )
        self.scent.pack(anchor="w", padx=25, pady=10)

        self.audio = ctk.CTkLabel(
            right,
            text="Audio: --",
            font=("Segoe UI",18)
        )
        self.audio.pack(anchor="w", padx=25, pady=10)

        self.status = ctk.CTkLabel(
            right,
            text="Status: Ready",
            font=("Segoe UI",18)
        )
        self.status.pack(anchor="w", padx=25, pady=10)

        button_frame = ctk.CTkFrame(right)
        button_frame.pack(fill="x", padx=20, pady=15)

        self.start_button = ctk.CTkButton(
    button_frame,
    text="Start Camera",
    command=self.start_system
)
        self.start_button.pack(fill="x", pady=5)

        self.demo_button = ctk.CTkButton(
            button_frame,
            text="Demo Recognition",
            command=self.demo_recognition
        )
        
        self.demo_button.pack(fill="x", pady=5)
        
        self.register_button = ctk.CTkButton(
            button_frame,
            text="Register Person",
            command=self.open_register
        )

        self.register_button.pack(fill="x", pady=5)

        self.history_btn = ctk.CTkButton(
            button_frame,
            text="Interaction History"
        )
        
        self.history_btn.pack(fill="x", pady=5)
        
        log_title = ctk.CTkLabel(
            right,
            text="System Activity",
            font=("Segoe UI", 18, "bold")
        )

        log_title.pack(anchor="w", padx=20, pady=(20, 5))

        self.log_box = ctk.CTkTextbox(
            right,
            width=320,
            height=180
        )

        self.log_box.pack(padx=20, pady=5)

        self.log_box.insert("end", "MemoryBridge started.\n")
        self.log_box.configure(state="disabled")
        
    def demo_recognition(self):

        name = random.choice(list(identity_map.keys()))
        person = identity_map[name]

        self.person.configure(
            text=f"Person: {name}"
        )

        self.relationship.configure(
            text=f"Relationship: {person['relationship']}"
        )

        self.scent.configure(
            text=f"Scent: {person['scent']}"
        )

        self.audio.configure(
            text=f"Audio: {person['audio']}"
        )

        self.status.configure(
            text=f"Status: {name} recognised successfully."
        )
        
        self.add_log(f"Demo recognition: {name}")
        
    def start_system(self):

        self.camera = Camera()
        
        load_faces()

        self.status.configure(
            text="Status: Camera Running"
        )

        self.add_log("Camera started.")
        
        self.start_button.configure(state="disabled")
        
        self.update_camera()
        
    def update_camera(self):

        if self.camera is None:
            return

        frame, faces = self.camera.get_frame()

        self.current_frame = frame
        
        if frame is not None:

            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            image = Image.fromarray(frame)

            image = image.resize((360, 320))

            photo = ImageTk.PhotoImage(image)

            self.camera_box.configure(
                image=photo,
                text=""
            )

            self.camera_box.image = photo

            if len(faces) > 0:
                self.status.configure(
                    text="Status: Face Detected"
                )

                if self.face_detected_time is None:
                    self.face_detected_time = time.time()

                elif time.time() - self.face_detected_time >= 2:

                    if not self.person_recognised:
                        name = recognise(self.current_frame)

                        if name is not None:

                            self.recognise_person(name)

                            self.person_recognised = True

                        else:

                            self.status.configure(
                                text="Status: Unknown Person"
                            )

                            self.add_log("Unknown face detected.")

                        

            else:
                self.face_detected_time = None
                self.person_recognised = False

                self.status.configure(
                    text="Status: Waiting for Face..."
                )

                self.progress.set(0)

                self.person.configure(
                    text="Person: Waiting..."
                )

                self.relationship.configure(
                    text="Relationship: --"
                )

                self.scent.configure(
                    text="Scent: --"
                )

                self.audio.configure(
                    text="Audio: --"
                )
        self.root.after(15, self.update_camera)
        
    def recognise_person(self):
        
        name = recognise(self.current_frame)

        if name is None:

            self.status.configure(
                text="Status: Unknown Person"
            )

            self.add_log("Unknown face detected.")

            return

        profile = identity_map[name]
        
        # Start recognition animation
        self.progress.set(0.2)
        self.root.update()
        time.sleep(0.3)

        self.progress.set(0.5)
        self.root.update()
        time.sleep(0.3)

        self.progress.set(0.8)
        self.root.update()
        time.sleep(0.3)

        self.progress.set(1.0)
        self.root.update()
            
        # Profile loading simulation
        name = recognise(self.current_frame)
        profile = identity_map[name]
        self.person.configure(
            text=f"Person: {name}"
        )
        
        self.add_log("Face recognised.")
        
        self.relationship.configure(
            text=f"Relationship: {profile['relationship']}"
        )
        
        self.add_log(f"Person identified: {name}")
        
        self.scent.configure(
            text=f"Scent: {profile['scent']}"
        )
        
        self.add_log(f"Scent selected: {profile['scent']}")
        
        self.audio.configure(
            text=f"Audio: {profile['audio']}"
        )
        
        self.add_log(f"Audio selected: {profile['audio']}")
        
        self.status.configure(
            text="Status: Memory Cue Activated."
        )   
        
        trigger_response(name)
        
        self.add_log("Interaction saved.")
        
        self.person_recognised = True
        
    def on_closing(self):

        if self.camera is not None:
            self.camera.release()

        self.root.destroy()