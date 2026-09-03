import os

import face_recognition


known_encodings = []
known_names = []


def load_faces():
    known_encodings.clear()
    known_names.clear()

    if not os.path.exists("faces"):
        return []

    for person in sorted(os.listdir("faces")):
        face_path = os.path.join("faces", person, "face.jpg")

        if not os.path.exists(face_path):
            continue

        image = face_recognition.load_image_file(face_path)
        encodings = face_recognition.face_encodings(image)

        if len(encodings) > 0:
            known_encodings.append(encodings[0])
            known_names.append(person)

    return known_names


def recognise(frame):
    if frame is None or len(frame) == 0:
        return None

    rgb = frame[:, :, ::-1]

    if not known_encodings:
        return None

    locations = face_recognition.face_locations(rgb)
    if not locations:
        return None

    encodings = face_recognition.face_encodings(rgb, locations)

    for encoding in encodings:
        matches = face_recognition.compare_faces(
            known_encodings,
            encoding,
            tolerance=0.5,
        )

        if True in matches:
            index = matches.index(True)
            return known_names[index]

    return None