import numpy as np
import cv2
import tensorflow as tf
import joblib

# ================= CONTRAST STRETCH =================
def contrast_stretch(gray):
    min_val = np.min(gray)
    max_val = np.max(gray)
    stretched = (gray - min_val) * (255.0 / (max_val - min_val))
    return np.clip(stretched, 0, 255).astype(np.uint8)

# ================= DESKEW ===========================
def rotate_image(image, angle):
    h, w = image.shape
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    return cv2.warpAffine(image, M, (w, h), borderValue=255)

def deskew_image(img):
    edges = cv2.Canny(img, 50, 150)
    lines = cv2.HoughLines(edges, 1, np.pi / 180, 150)
    if lines is None:
        return img

    rho, theta = lines[0][0]
    angle = np.rad2deg(theta) - 90 if theta > np.pi / 2 else -(90 - np.rad2deg(theta))
    return rotate_image(img, angle)

# ================= Preprocess =======================
def preprocess_image(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    contrast_img = contrast_stretch(gray)

    denoised = cv2.medianBlur(contrast_img, 3)

    deskewed = deskew_image(contrast_img)

    _, binary = cv2.threshold(
        deskewed, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU
    )
    return binary

# ================= LINE SEGMENTATION =================
def segment_lines(binary_img):
    horizontal_sum = np.sum(binary_img, axis=1)
    threshold = np.max(horizontal_sum) * 0.001

    line_images=[]
    in_line = False

    for i, val in enumerate(horizontal_sum):
        if val > threshold and not in_line:
            start = i
            in_line = True
        elif val <= threshold and in_line:
            end = i
            line_images.append(binary_img[start:end, :])
            in_line = False
    return line_images

# ================= Character SEGMENTATION =================
def segment_characters(lines):
    chars_list = []
    for line_img in lines:
        vertical_sum = np.sum(line_img, axis=0)
        threshold = np.max(vertical_sum) * 0.01

        chars = []
        in_char = False
        for x, val in enumerate(vertical_sum):
            if val > threshold and not in_char:
                start = x
                in_char = True
            elif val <= threshold and in_char:
                char_img = cv2.bitwise_not(line_img[:, start:x])
                chars.append(char_img)
                in_char = False
        chars_list.append(chars)
    return chars_list

def run_OCR(image_path):

    # LOAD MODEL 
    model = tf.keras.models.load_model(
        "Htun_ocr_cnn_best_model.h5"
    )

    # LOAD Label Encoder 
    label_encoder = joblib.load(
        "label_encoder.pkl"
    )

    # # Number of classes
    # num_classes = len(label_encoder.classes_)
    # print("Number of classes:", num_classes)
    
    # Preprocessing and Segmenting 
    image = cv2.imread(image_path)
    binary_img = preprocess_image(image)
    lines = segment_lines(binary_img)
    chars_list = segment_characters(lines)

    # print("Number of Lines: ", len(lines))
    # for chars in chars_list:
    #     i = 1
    #     print("Line ", i, ":", len(chars))

    # Doing OCR  
    ocr_results = []
    for chars in chars_list:

        line_text = ""

        for char_img in chars:
            resized = cv2.resize(char_img, (32, 32))
            resized = resized / 255.0
            input_img = np.expand_dims(resized, axis=(0, -1))
            pred = model.predict(input_img, verbose=0)
            label = label_encoder.inverse_transform([np.argmax(pred)])[0]
            line_text += label

        ocr_results.append(line_text)

    result = "\n".join(ocr_results)
    return result




