from database import ImageModel

import cv2, os
import logging
logger = logging.getLogger('gunicorn.error')


def video_to_images(path):
    cam = cv2.VideoCapture(path)
    root, file = os.path.split(path)
    filename = file.split('.')[0]

    try:
        directory = os.path.join(root, filename)
        if not os.path.exists(directory):
            os.makedirs(directory)
    except OSError:
        print('Error: Creating directory of data')
 
    currentframe = 0
    while True:
        ret, frame = cam.read()
        if ret:
            name = os.path.join(directory, filename + '_' + str(currentframe) + '.jpg')
            db_image = ImageModel.objects(path=name, deleted=False).first()
            if db_image is not None:
                continue

            cv2.imwrite(name, frame)
            currentframe += 1

            # try:
            #     image = ImageModel.create_from_path(name, dataset.id).save()
            #     thumbnail_generate_single_image.delay(image.id)
            # except:
        else:
            break
    
    cam.release()
    cv2.destroyAllWindows()