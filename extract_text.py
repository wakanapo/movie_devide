import cv2
import numpy as np

def extract_white(image):
    lower_white = np.array([240, 240, 240])
    upper_white = np.array([255, 255, 255])

    img_mask = cv2.inRange(image, lower_white, upper_white)
    _, img_mask = cv2.threshold(img_mask, 130, 255, cv2.THRESH_BINARY)
    return img_mask

def get_rects(mask):
    contours, _ = cv2.findContours(mask, cv2.RETR_TREE,
                                   cv2.CHAIN_APPROX_SIMPLE)[-2:]
    rects = []
    for contour in contours:
        approx = cv2.convexHull(contour)
        rect = cv2.boundingRect(approx)
        rects.append(np.array(rect))
    return rects

def draw_rects(rects, img, n):
    height, width = img.shape[:2]
    for rect in rects:
        if rect[2]*rect[3]>height*width/n:
            cv2.rectangle(img, tuple(rect[0:2]), tuple(rect[0:2]+rect[2:4]),
                          (0,0,255), thickness=2)
    return img

def cut_out_text(rects, img, n):
    height, width = img.shape[:2]
    new_rects = [rect for rect in rects
                 if rect[2] * rect[3] > height * width / n]
    if new_rects:
        min_x = min(new_rects, key=(lambda x: x[0]))
        min_y = min(new_rects, key=(lambda x: x[1]))
        max_w = max(new_rects, key=(lambda x: x[0] + x[2]))
        max_h = max(new_rects, key=(lambda x: x[1] + x[3]))
        max_rect = np.array([min_x[0], min_y[1], max_w[0] - min_x[0] + max_w[2],
                             max_h[1] - min_y[1] + max_h[3]])
        text_img = img[max_rect[1]:max_rect[1]+max_rect[3],
                       max_rect[0]:max_rect[0]+max_rect[2]]
    else:
        text_img = img
    return text_img

def run(img):
    paper_mask = extract_white(img)
    rects = get_rects(paper_mask)
#     fin_img = draw_rects(rects, img, 10000)
    fin_img = cut_out_text(rects, img, 10000)
    return fin_img

if __name__ == "__main__":
    image = cv2.imread('images00/image105.jpg')
    fin_img = run(image)
    cv2.imwrite('text00/image105.jpg', fin_img)
    cv2.imshow("TEXT", fin_img)
    while(1):
        if cv2.waitKey(10) > 0:
            break
