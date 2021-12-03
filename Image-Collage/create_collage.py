import os

from PIL import Image


def get_height_for_w(size_tuple: tuple, width: int):
    width, height = size_tuple
    aspect_ratio = width/height
    height = width / aspect_ratio
    return height

def get_image(width, location):
    image = Image.open(location).convert('RGBA')
    size_tuple = image.size
    height = get_height_for_w(size_tuple, width)
    image = image.resize((width, int(height)))
    return image

def create(directory, image_type):
    x_pos = 0
    y_pos = 0
    frame_w = 500
    border_w = 2
    border_h = 3
    image_paths = []
    
    # load required images from specified directory
    for file in os.listdir(directory):
        if file.endswith(f".{image_type}"):
            image_paths.append(os.path.join(directory, file))

    # calculate frame heght
    frame_h = get_image(frame_w, image_paths[0]).height

    # number of images to show per row
    num_horz_images = 4
    
    # calculate final image width and height
    img_w = (frame_w + border_w) * num_horz_images
    img_h = (frame_h + border_h) * (len(image_paths) // num_horz_images)
    
    print("Each frame size:", (frame_w, frame_h))
    print("Collage size:", (img_w, img_h))
    print(f"No. of Images: {len(image_paths)}")
    
    collage = Image.new("RGBA", (img_w,img_h), color=(255,255,255,255))

    # resize and paste images into main image (collage)
    for file in image_paths:
        if file.endswith(image_type):
            image = get_image(frame_w, os.path.join(directory, file))  # returns the resized PIL Image
            print((x_pos, y_pos), end=" | ")
            collage.paste(image, (x_pos, y_pos))
            if (x_pos + frame_w + border_w) < img_w:
                x_pos += frame_w + border_w
            else:
                x_pos = 0
                y_pos += frame_h + border_h
                print("\n", "---"*10)
    
    # save image (additionaly user can also enter output path using input prompt)
    collage.save("collage.png", bitmap_format="png")
    print("\ncollage saved\n")

def get_path():
    input_path = input("Enter path to locate images:")
    if os.path.exists(input_path):
        return input_path
    else:
        return get_path()

def get_image_type():
    types = ("png", "jpeg", "jpg", "webp")
    image_type = input("Enter image type to consider: ")
    if image_type in types:
        return image_type
    else:
        return get_image_type()

if __name__ == "__main__":
    img_path = get_path()
    img_type = get_image_type()
    create(img_path, img_type)
