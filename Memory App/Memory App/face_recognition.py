import face_recognition
import os


known_encodings = []
known_names = []


def load_faces():

    known_encodings.clear()
    known_names.clear()

    if not os.path.exists("faces"):
        return

    for person in os.listdir("faces"):

        image_path = os.path.join(
            "faces",
            person,
            "face.jpg"
        )

        if os.path.exists(image_path):

            image = face_recognition.load_image_file(
                image_path
            )

            encodings = face_recognition.face_encodings(
                image
            )

            if len(encodings) > 0:

                known_encodings.append(
                    encodings[0]
                )

                known_names.append(person)
                
def recognise(frame):

    rgb = frame[:, :, ::-1]

    locations = face_recognition.face_locations(rgb)

    encodings = face_recognition.face_encodings(
        rgb,
        locations
    )

    for encoding in encodings:

        matches = face_recognition.compare_faces(
            known_encodings,
            encoding,
            tolerance=0.5
        )

        if True in matches:

            index = matches.index(True)

            return known_names[index]

    return None