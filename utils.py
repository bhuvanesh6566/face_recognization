import face_recognition
import numpy as np

def get_face_encoding_from_file(file_stream):
    image = face_recognition.load_image_file(file_stream)
    encodings = face_recognition.face_encodings(image)
    if len(encodings) > 0:
        return encodings[0]
    return None

def identify_user(live_encoding, known_users):
    if not known_users:
        return None
    known_encodings = [u[1] for u in known_users]
    known_ids = [u[0] for u in known_users]

    matches = face_recognition.compare_faces(known_encodings, live_encoding, tolerance=0.5)
    face_distances = face_recognition.face_distance(known_encodings, live_encoding)
    best_match_index = np.argmin(face_distances)

    if matches[best_match_index]:
        return known_ids[best_match_index]
    return None