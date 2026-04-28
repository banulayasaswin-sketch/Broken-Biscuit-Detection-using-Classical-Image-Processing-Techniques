import cv2
import numpy as np
import os

 
 1. PATHS & DIRECTORY SETU 

 Your current folder:
 D:\USER\Downloads\1234\input_image

input_folder = r"D:\USER\Downloads\1234\input_image"
output_folder = r"D:\USER\Downloads\1234\output_images"

 Create output folder if it doesn't exist
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

 Load all images from the input_image folder
image_files = [
    f for f in os.listdir(input_folder)
    if f.lower().endswith(('.png', '.jpg', '.jpeg'))
]

if not image_files:
    print(f"No images found in {input_folder}")
    exit()

for file_name in image_files:
    img_path = os.path.join(input_folder, file_name)
    image = cv2.imread(img_path)

    if image is None:
        print(f"Could not read: {file_name}")
        continue

    output = image.copy()

    
     2. PREPROCESSING (COLOR MASKING)
     
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

     Broad range to catch light and dark toasted areas
    lower = np.array([5, 30, 40])
    upper = np.array([45, 255, 255])
    mask = cv2.inRange(hsv, lower, upper)

     Clean the mask to make biscuits solid blobs
    kernel = np.ones((7, 7), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=2)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=1)

     Find contours
    contours, _ = cv2.findContours(
        mask,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE
    )

     Calculate max area to help filter small fragments
    areas = [
        cv2.contourArea(c)
        for c in contours
        if cv2.contourArea(c) > 3000
    ]

    max_area = max(areas) if areas else 0

    intact_count = 0
    broken_count = 0

     
     3. PROCESSING EACH BISCUIT
     
    for cnt in contours:
        area = cv2.contourArea(cnt)

         Ignore small crumbs
        if area < 3000:
            continue

          Shape Scores 

         Circle Score
        (xc, yc), radius = cv2.minEnclosingCircle(cnt)
        circle_area = np.pi * radius * radius
        circle_score = area / circle_area if circle_area > 0 else 0

         Rotated Rectangle Score
        rect = cv2.minAreaRect(cnt)
        rw, rh = rect[1]
        rotated_rect_area = rw * rh if (rw > 0 and rh > 0) else 0
        rotated_rect_score = (
            area / rotated_rect_area
            if rotated_rect_area > 0 else 0
        )

         Solidity Score
        hull = cv2.convexHull(cnt)
        hull_area = cv2.contourArea(hull)
        solidity = area / hull_area if hull_area > 0 else 0

          Classification 

        best_shape_match = max(circle_score, rotated_rect_score)

        is_correct_shape = best_shape_match > 0.85
        is_solid = solidity > 0.96
        is_full_size = area > (max_area * 0.75)

        x, y, w, h = cv2.boundingRect(cnt)

        if is_correct_shape and is_solid and is_full_size:
            label = "Intact Biscuit"
            color = (0, 255, 0)  # Green
            intact_count += 1
        else:
            label = "Broken Biscuit"
            color = (0, 0, 255)  # Red
            broken_count += 1

         
         4. DRAW RESULTS
         
        cv2.drawContours(output, [cnt], -1, color, 3)
        cv2.rectangle(output, (x, y), (x + w, y + h), color, 2)

        cv2.putText(
            output,
            label,
            (x, y - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            color,
            2
        )

     Save output image
    save_name = f"result_{file_name}"
    save_path = os.path.join(output_folder, save_name)
    cv2.imwrite(save_path, output)

    print(
        f"Processed {file_name}: "
        f"Intact={intact_count}, Broken={broken_count}"
    )

print("\nAll images processed successfully.")
print("Check the folder: D:\\USER\\Downloads\\1234\\output_images")
