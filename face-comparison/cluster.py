from scipy import misc
import numpy as np
import os
import json
from glob import glob
import sys
import argparse
import base64
from sklearn.cluster import DBSCAN
from PIL import Image
import cv2
import io
# Take in base64 string and return PIL image


def toRGB(image):
    return cv2.cvtColor(np.array(image), cv2.COLOR_BGR2RGB)


def stringToImage(base64_string):
    imgdata = base64.b64decode(base64_string)
    return Image.open(io.BytesIO(imgdata))


def load_data(folder):
    data = []
    pattern = os.path.join(folder, '*.json')
    for file_name in glob(pattern):
        print(file_name)
        with open(file_name) as f:
            data.append(json.load(f))
    return data


def save_image(data,embedding_map, index,cnt,path):
    indices = embedding_map[index]
    base_image = stringToImage(data[indices[0]]['image'])
    prediction = data[indices[0]]['predictions'][indices[1]]
    image = toRGB(base_image)
    cropped = image[prediction['top']:prediction['bottom'],
                                        prediction['left']:prediction['right']]
    face_bb = data[indices[0]]['predictions'][indices[1]]['faces'][indices[2]]['bounding_box']
    frame = toRGB(cropped)
    cv2.rectangle(frame,
                  (face_bb[0], face_bb[1]), (face_bb[2], face_bb[3]),
                  (0, 255, 0), 2)
    cv2.imwrite(os.path.join(path, str(cnt) + '.png'), frame)


def main(args):

    data = load_data('./samples')
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
                        print((f_index, p_index, d_index))

    nrof_images = len(embeddings)

    matrix = np.zeros((nrof_images, nrof_images))

    print('')
    # Print distance matrix
    print('Distance matrix')
    print('    ', end='')
    for i in range(nrof_images):
        print('    %1d     ' % i, end='')
    print('')
    for i in range(nrof_images):
        print('%1d  ' % i, end='')
        for j in range(nrof_images):
            dist = np.sqrt(
                np.sum(np.square(np.subtract(embeddings[i], embeddings[j]))))
            matrix[i][j] = dist
            print('  %1.4f  ' % dist, end='')
        print('')

    print('')

    # DBSCAN is the only algorithm that doesn't require the number of clusters to be defined.
    db = DBSCAN(eps=args.cluster_threshold,
                min_samples=args.min_cluster_size, metric='precomputed')
    db.fit(matrix)
    labels = db.labels_

    # get number of clusters
    no_clusters = len(set(labels)) - (1 if -1 in labels else 0)

    print('No of clusters:', no_clusters)

    if no_clusters > 0:
        if args.largest_cluster_only:
            largest_cluster = 0
            for i in range(no_clusters):
                print('Cluster {}: {}'.format(i, np.nonzero(labels == i)[0]))
                if len(np.nonzero(labels == i)[0]) > len(np.nonzero(labels == largest_cluster)[0]):
                    largest_cluster = i
            print('Saving largest cluster (Cluster: {})'.format(largest_cluster))
            cnt = 1
            for i in np.nonzero(labels == largest_cluster)[0]:
                save_image(data,embedding_map,i,cnt,args.out_dir)
                cnt += 1
        else:
            print('Saving all clusters')
            for i in range(no_clusters):
                cnt = 1
                print('Cluster {}: {}'.format(i, np.nonzero(labels == i)[0]))
                path = os.path.join(args.out_dir, str(i))
                if not os.path.exists(path):
                    os.makedirs(path)
                    for j in np.nonzero(labels == i)[0]:
                        save_image(data,embedding_map,j,cnt,path )
                        cnt += 1
                else:
                    for j in np.nonzero(labels == i)[0]:
                        save_image(data,embedding_map,j,cnt,path )
                        cnt += 1


def parse_arguments(argv):
    parser = argparse.ArgumentParser()
    # parser.add_argument('data_dir', type=str,
    #                     help='The directory containing the images to cluster into folders.')
    parser.add_argument(
        '--out_dir', help='The output directory where the image clusters will be saved.', default="./cluster")
    parser.add_argument('--largest_cluster_only', action='store_true',
                        help='This argument will make that only the biggest cluster is saved.')
    parser.add_argument('--min_cluster_size', type=int,
                        help='The minimum amount of pictures required for a cluster.', default=1)
    parser.add_argument('--cluster_threshold', type=float,
                        help='The minimum distance for faces to be in the same cluster', default=1.0)

    return parser.parse_args(argv)


if __name__ == '__main__':
    main(parse_arguments(sys.argv[1:]))
