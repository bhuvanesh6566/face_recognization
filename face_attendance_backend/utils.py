import face_recognition
import numpy as np

def get_face_encoding_from_file(file_stream):
    """
    Reads an image file stream and returns the 128-d face encoding.
    Returns None if no face is found.
    """
    # Load image using face_recognition
    image = face_recognition.load_image_file(file_stream)
    
    # Get encodings (assuming only one face per registration image)
    encodings = face_recognition.face_encodings(image)
    
    if len(encodings) > 0:
        return encodings[0]
    return None

def identify_user(live_encoding, known_users):
    """
    Compares live encoding against a list of known users from DB.
    known_users format: [(user_id, encoding_array), ...]
    Returns user_id if match found, else None.
    """
    if not known_users:
        return None

    known_encodings = [u[1] for u in known_users]
    known_ids = [u[0] for u in known_users]

    # Compare faces (tolerance 0.6 is standard)
    matches = face_recognition.compare_faces(known_encodings, live_encoding, tolerance=0.5)
    
    # Calculate distances to find the *best* match
    face_distances = face_recognition.face_distance(known_encodings, live_encoding)
    
    # Get the index of the best match (smallest distance)
    best_match_index = np.argmin(face_distances)

    if matches[best_match_index]:
        return known_ids[best_match_index]
    
    return None