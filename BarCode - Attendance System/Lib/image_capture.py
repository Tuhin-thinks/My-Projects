from pyzbar import pyzbar
import cv2
import os

for k, v in os.environ.items():
    if k.startswith("QT_") and "cv2" in v:
        del os.environ[k]


def decide_actual_data(response: dict):
    freq_table = {}
    for data in response['Data']:
        data: bytes
        if data in freq_table.keys():
            freq_table[data] += 1
        else:
            freq_table[data] = 1

    max_v = 1
    actual_data = b''

    print("[*] Frequency table:", freq_table)
    print()
    for k, v in freq_table.items():
        if v > max_v:
            max_v = v
            actual_data = k
    return actual_data


def decode(image, response: dict):
    """
    decode rectangle over barcode from image and returns updated storage dict and the image object
    """
    decoded_objects = pyzbar.decode(image)
    for obj in decoded_objects:

        # draw the rectangle
        image = draw_barcode(obj, image)
        if "Data" in response.keys():
            response['Data'].append(obj.data)
        else:
            response['Type'] = obj.type
        if "Type" in response.keys():
            response['Type'].append(obj.type)
        else:
            response['Type'] = [obj.type]
    return image, response


def draw_barcode(decoded, image):
    # uncomment above and comment below if you want to draw a polygon and not a rectangle
    image = cv2.rectangle(image, (decoded.rect.left, decoded.rect.top),
                          (decoded.rect.left + decoded.rect.width, decoded.rect.top + decoded.rect.height),
                          color=(18, 243, 243),
                          thickness=3)
    return image


def main(LIMIT, *args):
    # Read the video from specified path
    process_image = args[0]

    cam = cv2.VideoCapture(0)

    try:

        # creating a folder named data
        if not os.path.exists('data'):
            os.makedirs('data')

        # if not created then raise error
    except OSError:
        print('Error: Creating directory of data')

    # frame
    currentframe = 0
    capture_res = {'Data': []}
    while True:

        # reading image from webcam
        ret, frame = cam.read()

        if not cv2.waitKey(1) & 0xFF == ord('q'):

            cv2.namedWindow('Video Capture Feed', cv2.WINDOW_NORMAL)
            cv2.resizeWindow('Video Capture Feed', 600, 600)

            position = (0, 30)  # text top-left corner
            decoded_img, capture_res = decode(frame, capture_res)
            cv2.putText(
                decoded_img,
                f"Successful Captures : {len(capture_res['Data'])}",  # text
                position,  # position at which writing has to start
                cv2.FONT_HERSHEY_SIMPLEX,
                1,  # font size
                (0, 255, 255, 255),  # font color
                1,  # font stroke
                cv2.LINE_AA  # this is just to make font look better (as per docs)
            )
            position = (350, 420)  # position for quit-info text
            cv2.putText(
                decoded_img,
                f"Press Q to exit image capture feed",  # text
                position,  # position at which writing has to start
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,  # font size
                (0, 0, 255, 255),  # font color
                2,  # font stroke
                cv2.LINE_AA  # this is just to make font look better (as per docs)
            )
            cv2.imshow('Video Capture Feed', decoded_img)

            currentframe += 1
            if len(capture_res['Data']) >= LIMIT:  # 20 frames of decoded data
                data = decide_actual_data(capture_res)
                print(f"Actual Data:{data}")
                process_image(data)
                currentframe = 0
                capture_res['Data'] = []
        else:
            break

    # Release all space and windows once done
    cam.release()
    cv2.destroyAllWindows()
