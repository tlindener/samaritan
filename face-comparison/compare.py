""" Face Cluster """

import numpy as np
import argparse
import face
import os
from glob import glob
import json
import cv2
def face_distance(face_encodings, face_to_compare):
    """
    Given a list of face encodings, compare them to a known face encoding and get a euclidean distance
    for each comparison face. The distance tells you how similar the faces are.
    :param faces: List of face encodings to compare
    :param face_to_compare: A face encoding to compare against
    :return: A numpy ndarray with the distance for each face in the same order as the 'faces' array
    """
    import numpy as np
    if len(face_encodings) == 0:
        return np.empty((0))

    #return 1/np.linalg.norm(face_encodings - face_to_compare, axis=1)
    return np.sum(face_encodings*face_to_compare,axis=1)


def parse_args():
    """Parse input arguments."""
    import argparse
    parser = argparse.ArgumentParser(description='Get a shape mesh (t-pose)')
    args = parser.parse_args()

    return args
def receive_embeddings(data):

    embeddings = []
    embedding_map = {}
    for f_index, frame in enumerate(data):
        print(f_index)
        for p_index, prediction in enumerate(frame["predictions"]):
            if prediction["label"] == "person":
                if "faces" in prediction:
                    for d_index, face in enumerate(prediction["faces"]):
                        embeddings.append(face["embedding"])
                        embedding_map[len(embeddings) -
                                      1] = (f_index, p_index, d_index)
    return embeddings,embedding_map

def load_data(folder):
    data = []
    pattern = os.path.join(folder, '*.json')
    for file_name in glob(pattern):
        print(file_name)
        with open(file_name) as f:
            data.append(json.load(f))
    return data

def main(args):
    face_recognition = face.Recognition()
    data = load_data('./samples')
    embeddings,embedding_map = receive_embeddings(data)
    img = cv2.imread("./images/cameron.jpg")
    faces = face_recognition.identify(img)
    distance = face_distance(embeddings,faces[0].embedding)
    print(distance)


if __name__ == '__main__':
    """ Entry point """
    main(parse_args())
