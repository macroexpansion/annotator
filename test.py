from PIL import Image
import cv2
import os

videos = ['videotest/video1.mp4', 'videotest/video2.mp4', 'videotest/video2/video2-0.jpg']

def cv2_video(path):
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
            # cv2.imwrite(name, frame)

            currentframe += 1
        else:
            break
    
    cam.release()
    cv2.destroyAllWindows()


def test(directory):
    count = 1
    toplevel = list(os.listdir(directory))
    for root, dirs, files in os.walk(directory):
        print(f'toplevel: {toplevel}')
        print(f'root: {root}')
        print(f'dirs: {dirs}')
        print(f'files: {files}')
        if root.split('/')[-1].startswith('.'):
            continue

        try:
            youarehere = toplevel.index(root.split('/')[-1])
            progress = int((youarehere / len(toplevel)) * 100)
            print(f'progress: {progress}')
        except:
            pass

        print('------')
        if count == 6:
            break

        count += 1

if __name__ == '__main__':
    # for path in videos:
    #     cv2_video(path)
    
    # test('storage/datasets/  dsdsadsa')

    cam = cv2.VideoCapture('videotest/video1/video1_0.jpg')
    # cam = cv2.VideoCapture('videotest/sample_1280x720.m4v')
    while True:
        ret, frame = cam.read()
        print(ret)
        cv2.imwrite('dsadsada.jpg', frame)

        if ret:
            pass
        else:
            break
