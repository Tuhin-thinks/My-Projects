import os
import re
import statistics as stats
import sys
import typing
from functools import lru_cache

from PIL import Image  # requires installation !pip install pillow
from tqdm import tqdm

Image.MAX_IMAGE_PIXELS = (
    None  # setting this value to compress images having size of 600MB+
)


def optimize_image(inp_path, size_tuple, op_path):
    if os.path.exists(inp_path):
        print("\n[+] Loading image...")
        image_ = Image.open(inp_path)
        print("[+] image loaded\n")

        print("[+] Resizing image...")
        image_ = image_.resize(size_tuple, Image.ANTIALIAS)
        print("[+] image resized\n")

        print("[+] Saving image...")
        image_.save(op_path, optimize=True, quality=90)
        print("Image saved successfully\n")


def get_height_for_w(size_tuple: tuple, width: int):
    width_img, height_img = size_tuple
    aspect_ratio = width_img / height_img
    height = width / aspect_ratio
    return height


def get_width_for_height(size_tuple: tuple, height: int):
    width_img, height_img = size_tuple
    aspect_ratio = width_img / height_img
    width = height * aspect_ratio
    return width


def get_image(required_width, required_height, location):
    """Utiliyt function to get the resized image that exactly fits inside the box given

    Args:
        required_width: width of each image frame inside collage
        required_height: height of the image frame inside collage
    """

    image = Image.open(location).convert("RGBA")
    size_tuple = image.size
    height = get_height_for_w(size_tuple, required_width)
    required_height_ = required_height or int(height)
    image = image.resize((required_width, required_height_))
    return image


def get_n_files(target_dir):
    """Get number of files in the target directory

    Args:
        :param target_dir: directory to scan for number of files
    """
    return len(
        [
            x
            for x in os.listdir(target_dir)
            if os.path.isfile(os.path.join(target_dir, x))
        ]
    )


def create(directory, image_type: typing.Union[str, typing.List]):
    """Primary working function for creating collage and calculations"""

    x_pos = 0
    y_pos = 0
    frame_w = 500
    border_w = 2
    border_h = 2
    image_paths = []

    # load required images from specified directory
    for file in os.listdir(directory):
        if isinstance(image_type, str) and file.endswith(f".{image_type}"):
            image_paths.append(os.path.join(directory, file))
        elif isinstance(image_type, typing.List) and any(
            (file.lower().endswith(x) for x in image_type)
        ):
            image_paths.append(os.path.join(directory, file))

    # calculate frame heght
    # ------------- calculate max frame height --------
    # gen_frame_heights = [
    #     get_image(frame_w, None, img_path).height for img_path in image_paths
    # ]
    # mode_frame_h = int(
    #     max(gen_frame_heights)
    # )  # modify and assign this value to mode_frame_h, if you want to use some other box height for each image
    frame_h = 500  # frame height for each image

    # ------------> number of images to show per row <----------------
    num_horz_images = (
        int(
            input(
                f"\n{len(image_paths)} images to be used in collage,\n"
                f"Enter number of images per row of the collage: "
            )
        )
        or 5
    )  # if user enters 0, program will paste 5 images per row.

    # ------------> calculate collage image width and height <---------------
    img_w = (frame_w + border_w) * num_horz_images
    img_h = (frame_h + border_h) * (len(image_paths) // num_horz_images)

    # ------------------ print collage image informations ----------------
    print(
        f"""
Each frame size: {(frame_w, frame_h)}
Collage size:    {(img_w, img_h)}
No. of Images:   {len(image_paths)}
"""
    )

    # ------------ create empty collage image ---------------
    collage = Image.new("RGBA", (img_w, img_h), color=(255, 255, 255, 255))

    # resize and paste images into main image (collage)
    for file in tqdm(image_paths, desc="Progress: "):
        image = get_image(frame_w, None, file)  # returns the resized PIL Image

        # print(
        #     f"({x_pos}:{image.width},{y_pos}:{image.height})", end=" | "
        # )  # this print the top-left position of each child image inside collage image.

        collage.paste(image, (x_pos, y_pos))
        if (x_pos + frame_w + border_w) < img_w:
            x_pos += frame_w + border_w
        else:
            x_pos = 0
            y_pos += frame_h + border_h
            # print("\n", "---" * 2 * num_horz_images)

    # save image (additionaly user can also enter output path using input prompt)
    collage_file_name = f"collage{get_n_files(os.getcwd())}.png"
    collage.save(collage_file_name, bitmap_format="png")
    print(f"\ncollage saved as {os.path.realpath(collage_file_name)}\n")


def get_path():
    """Get path to scan images from."""

    input_path = input(
        "Enter path to locate images [suffix :relpath for entering relative paths] :"
    )
    if input_path.endswith(":relpath"):
        match_pattern = r"(.*)\:relpath$"
        input_path = os.path.realpath(re.search(match_pattern, input_path).groups()[0])
        print(f"  Generated realpath: {input_path}")
    if os.path.exists(input_path):
        return input_path
    else:
        return get_path()


def get_image_type():
    """Get image type to consider for the collage image."""

    types = ("png", "jpeg", "jpg", "webp")
    image_type = input(
        "Enter image type to consider: [Enter ; separated values for mutiple types]: "
    )
    if image_type in types:
        return image_type
    elif ";" in image_type:
        return image_type.strip().split(";")
    else:
        return get_image_type()


if __name__ == "__main__":
    argv = sys.argv
    mode = "create"
    if len(argv) == 2:
        mode = argv[1]
    if mode == "create":
        img_path = get_path()
        img_type = get_image_type()
        create(img_path, img_type)
    elif mode == "optimize":
        img_to_optimize = input("Enter image path to optimize: ")
        save_path = input("Enter image save path: ")
        size_tuple = tuple(
            map(
                int,
                input("Enter size tuple to resize image (space separated): ").split(
                    " "
                ),
            )
        )
        optimize_image(img_to_optimize, size_tuple, save_path)
