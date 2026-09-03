import os
import random
import time

import cv2
import customtkinter as ctk
from PIL import Image, ImageTk

from camera import Camera
from face_recognition_module import load_faces, recognise
from identity_database import DEFAULT_SCENTS, identity_map, load_people, save_people
from response_engine import trigger_response


ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")


class MemoryBridgeGUI:

    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("MemoryBridge")
        self.root.geometry("1100x750")
        self.root.resizable(False, False)

        self.camera = None
        self.current_frame = None
        self.face_detected_time = None
        self.person_recognised = False
        self.captured_frame = None
        self.register = None

        self.build_gui()
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()

    def add_log(self, message):
        if not hasattr(self, "log_box"):
            return

        self.log_box.configure(state="normal")
        self.log_box.insert("end", message + "\n")
        self.log_box.see("end")
        self.log_box.configure(state="disabled")

    def set_status(self, text):
        if hasattr(self, "status"):
            self.status.configure(text=text)

    def open_register(self):
        self.register = ctk.CTkToplevel(self.root)
        self.register.title("Register Person")
        self.register.geometry("450x650")

        ctk.CTkLabel(
            self.register,
            text="Register New Person",
            font=("Segoe UI", 24, "bold"),
        ).pack(pady=20)

        self.register_camera = ctk.CTkLabel(
            self.register,
            text="Camera Preview",
            width=250,
            height=220,
            fg_color="#d9d9d9",
        )
        self.register_camera.pack(pady=15)

        self.name_entry = ctk.CTkEntry(self.register, placeholder_text="Name")
        self.name_entry.pack(fill="x", padx=30, pady=10)

        self.scent_var = ctk.StringVar(value="")
        self.scent_combo = ctk.CTkComboBox(
            self.register,
            values=DEFAULT_SCENTS,
            variable=self.scent_var,
            state="readonly",
        )
        self.scent_combo.pack(fill="x", padx=30, pady=10)

        self.audio_entry = ctk.CTkEntry(
            self.register,
            placeholder_text="Optional audio filename or path",
        )
        self.audio_entry.pack(fill="x", padx=30, pady=10)

        ctk.CTkButton(
            self.register,
            text="Capture Face",
            command=self.capture_face,
        ).pack(pady=10)

        ctk.CTkButton(
            self.register,
            text="Save Person",
            command=self.save_person,
        ).pack(pady=20)

    def capture_face(self):
        if self.camera is None:
            self.camera = Camera()

        frame, faces = self.camera.get_frame()

        if frame is None:
            self.set_status("Status: Camera unavailable.")
            return

        if len(faces) == 0:
            self.set_status("Status: No face detected. Please try again.")
            return

        self.captured_frame = frame.copy()
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image = Image.fromarray(rgb).resize((250, 220))
        photo = ctk.CTkImage(light_image=image, dark_image=image, size=(250, 220))

        self.register_camera.configure(image=photo, text="")
        self.register_camera.image = photo
        self.set_status("Status: Face captured. Please review and save.")

    def save_person(self):
        name = self.name_entry.get().strip()
        scent = self.scent_var.get().strip()
        audio = self.audio_entry.get().strip()

        if not name:
            self.set_status("Status: Please enter a name.")
            return

        if self.captured_frame is None:
            self.set_status("Status: Please capture a face before saving.")
            return

        if not scent:
            self.set_status("Status: Please choose a scent.")
            return

        folder = os.path.join("faces", name)
        os.makedirs(folder, exist_ok=True)

        photo_path = os.path.join(folder, "face.jpg")
        cv2.imwrite(photo_path, self.captured_frame)

        identity_map[name] = {
            "scent": scent,
            "audio": audio,
        }

        save_people()
        load_faces()

        self.add_log(f"{name} registered.")
        self.set_status(f"Status: {name} saved successfully.")

        if self.register is not None:
            self.register.destroy()
            self.register = None

    def build_gui(self):
        title = ctk.CTkLabel(
            self.root,
            text="MemoryBridge",
            font=("Segoe UI", 34, "bold"),
        )
        title.pack(pady=(20, 5))

        subtitle = ctk.CTkLabel(
            self.root,
            text="Multimodal Memory Support Prototype",
            font=("Segoe UI", 18),
        )
        subtitle.pack()

        main_frame = ctk.CTkFrame(self.root)
        main_frame.pack(fill="both", expand=True, padx=30, pady=25)

        left = ctk.CTkFrame(main_frame, width=420)
        left.pack(side="left", fill="both", expand=True, padx=15, pady=15)

        camera_title = ctk.CTkLabel(
            left,
            text="Camera Preview",
            font=("Segoe UI", 22, "bold"),
        )
        camera_title.pack(pady=10)

        self.camera_box = ctk.CTkLabel(
            left,
            text="Camera not started",
            width=360,
            height=320,
            fg_color="#d9d9d9",
            corner_radius=12,
        )
        self.camera_box.pack(pady=15)

        self.progress = ctk.CTkProgressBar(left)
        self.progress.pack(pady=10)
        self.progress.set(0)

        right = ctk.CTkFrame(main_frame)
        right.pack(side="right", fill="both", expand=True, padx=15, pady=15)

        info = ctk.CTkLabel(
            right,
            text="Recognition Details",
            font=("Segoe UI", 22, "bold"),
        )
        info.pack(pady=10)

        self.person = ctk.CTkLabel(
            right,
            text="Person: Waiting...",
            font=("Segoe UI", 18),
        )
        self.person.pack(anchor="w", padx=25, pady=10)

        self.scent = ctk.CTkLabel(
            right,
            text="Assigned scent: --",
            font=("Segoe UI", 18),
        )
        self.scent.pack(anchor="w", padx=25, pady=10)

        self.audio = ctk.CTkLabel(
            right,
            text="Audio: Not assigned",
            font=("Segoe UI", 18),
        )
        self.audio.pack(anchor="w", padx=25, pady=10)

        self.status = ctk.CTkLabel(
            right,
            text="Status: Ready",
            font=("Segoe UI", 18),
        )
        self.status.pack(anchor="w", padx=25, pady=10)

        button_frame = ctk.CTkFrame(right)
        button_frame.pack(fill="x", padx=20, pady=15)

        self.start_button = ctk.CTkButton(
            button_frame,
            text="Start Camera",
            command=self.start_system,
        )
        self.start_button.pack(fill="x", pady=5)

        self.demo_button = ctk.CTkButton(
            button_frame,
            text="Demo Recognition",
            command=self.demo_recognition,
        )
        self.demo_button.pack(fill="x", pady=5)

        self.register_button = ctk.CTkButton(
            button_frame,
            text="Register Person",
            command=self.open_register,
        )
        self.register_button.pack(fill="x", pady=5)

        self.history_btn = ctk.CTkButton(
            button_frame,
            text="Interaction History",
        )
        self.history_btn.pack(fill="x", pady=5)

        log_title = ctk.CTkLabel(
            right,
            text="System Activity",
            font=("Segoe UI", 18, "bold"),
        )
        log_title.pack(anchor="w", padx=20, pady=(20, 5))

        self.log_box = ctk.CTkTextbox(right, width=320, height=180)
        self.log_box.pack(padx=20, pady=5)
        self.log_box.insert("end", "MemoryBridge started.\n")
        self.log_box.configure(state="disabled")

    def demo_recognition(self):
        if not identity_map:
            self.person.configure(text="Person: Waiting...")
            self.scent.configure(text="Assigned scent: --")
            self.audio.configure(text="Audio: Not assigned")
            self.set_status("Status: No registered people.")
            self.add_log("No profiles available for demo recognition.")
            return

        name = random.choice(list(identity_map.keys()))
        profile = identity_map[name]
        scent = profile.get("scent", "--")
        audio = profile.get("audio", "")

        self.person.configure(text=f"Person: {name}")
        self.scent.configure(text=f"Assigned scent: {scent}")
        self.audio.configure(text=f"Audio: {'Available' if audio else 'Not assigned'}")
        self.set_status(f"Status: {name} recognised successfully.")
        self.add_log(f"Demo recognition: {name}")

    def start_system(self):
        self.camera = Camera()
        load_people()
        load_faces()

        self.set_status("Status: Camera Running")
        self.add_log("Camera started.")
        self.start_button.configure(state="disabled")
        self.update_camera()

    def update_camera(self):
        if self.camera is None:
            return

        frame, faces = self.camera.get_frame()
        self.current_frame = frame

        if frame is not None:
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image = Image.fromarray(rgb).resize((360, 320))
            photo = ImageTk.PhotoImage(image)

            self.camera_box.configure(image=photo, text="")
            self.camera_box.image = photo

            if len(faces) > 0:
                if self.face_detected_time is None:
                    self.face_detected_time = time.time()

                elif time.time() - self.face_detected_time >= 2 and not self.person_recognised:
                    name = recognise(self.current_frame)

                    if name is not None:
                        self.recognise_person(name)
                    else:
                        self.person.configure(text="Person: Unknown")
                        self.scent.configure(text="Assigned scent: --")
                        self.audio.configure(text="Audio: Not assigned")
                        self.set_status("Status: Unknown person")
                        self.add_log("Unknown person")

            else:
                self.face_detected_time = None
                self.person_recognised = False
                self.person.configure(text="Person: Waiting...")
                self.scent.configure(text="Assigned scent: --")
                self.audio.configure(text="Audio: Not assigned")
                self.set_status("Status: No recognised person")
                self.progress.set(0)

        self.root.after(15, self.update_camera)

    def recognise_person(self, name=None):
        if name is None:
            name = recognise(self.current_frame)

        if name is None:
            self.set_status("Status: Unknown person")
            self.add_log("Unknown person")
            return

        profile = identity_map.get(name)
        if profile is None:
            self.set_status("Status: Unknown person")
            self.add_log(f"No profile found for {name}")
            return

        scent = profile.get("scent", "--")
        audio = profile.get("audio", "")

        self.progress.set(1.0)
        self.person.configure(text=f"Person: {name}")
        self.scent.configure(text=f"Assigned scent: {scent}")
        self.audio.configure(text=f"Audio: {'Available' if audio else 'Not assigned'}")
        self.set_status(f"Status: Scent trigger activated: {scent}")

        self.add_log(f"Person recognised: {name}")
        self.add_log(f"Assigned scent: {scent}")
        trigger_response(name)
        self.person_recognised = True

    def on_closing(self):
        if self.camera is not None:
            self.camera.release()

        self.root.destroy()