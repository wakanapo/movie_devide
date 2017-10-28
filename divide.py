import cv2
from PIL import Image
import numpy as np
import os
import pandas as pd
from tqdm import tqdm
import matplotlib.pyplot as plt
import mojimoji

import extract_text
import google_ocr

# def ocr(image):
#     tools = pyocr.get_available_tools()
#     if len(tools) == 0:
#         print("No OCR tool found")
#         sys.exit(1)
#     # The tools are returned in the recommended order of usage
#     tool = tools[0]
    
#     text = tool.image_to_string(
#         Image.open(image),
#         lang="jpn",
#         builder=pyocr.builders.TextBuilder(tesseract_layout=6)
#     )
#     return text

def whitehist(rects, mask, n):
    text_area = extract_text.cut_out_text(rects, mask, 100000)
    text_area = cv2.resize(text_area, (150, 150))
    m_sum = np.sum(text_area/255, axis=0)
    if max(m_sum) != 0:
        m_sum /= max(m_sum)
    return m_sum

def isChange(x, y):
    if np.corrcoef(x, y)[0, 1] < 0.6 or np.sum(y) == 0:
        return True
    return False

def find_devide_point(dirId, n):
    dirpath =  "images{0:02d}".format(dirId) 
    df = pd.DataFrame(index=[], columns=['id', 'time', 'text', 'state'])
    imId = 1
    state = 0  # text: exist = 1, none = 0
    y = np.zeros(150)
    pbar = tqdm(total=120)
    cnt = 0
    hists = np.array([])
    before_text = ""
    while(os.path.isfile(dirpath+"/image{}.jpg".format(imId))):
        pbar.update(1)
        path = dirpath+"/image{}.jpg".format(imId)
        img = cv2.imread(path)
        mask = extract_text.extract_white(img)
        rects = extract_text.get_rects(mask)
        height, width = img.shape[:2]
        rects = [rect for rect in rects
                if rect[2] * rect[3] > height * width / n]

        # textが存在しない場合
        if not rects:
            if state:
                state = 0
                y = np.zeros(150)
                series = pd.Series([imId-1, (imId-1)*0.5, before_text, -1], index=df.columns)
                df = df.append(series, ignore_index=True)
            imId += 1
            continue
        x = whitehist(rects, mask, n)
        min_x = min(rects, key=(lambda x: x[0]))
        min_y = min(rects, key=(lambda x: x[1]))
        max_w = max(rects, key=(lambda x: x[0] + x[2]))
        max_h = max(rects, key=(lambda x: x[1] + x[3]))
        max_rect = np.array([min_x[0], min_y[1], max_w[0] - min_x[0] + max_w[2],
                             max_h[1] - min_y[1] + max_h[3]])
        
        # 画面がホワイトアウトした場合
        if max_rect[2] * max_rect[3] >= height * width:
            if state:
                state = 0
                y = x
                series = pd.Series([imId-1, (imId-1)*0.5, before_text, -1], index=df.columns)
                df = df.append(series, ignore_index=True)
            imId += 1
            continue

        if isChange(x, y):
            cnt += 1
            text = google_ocr.detect_text(dirId, imId)
            text = text.replace(" ", "").replace("\n", "").replace(u'　', "").replace("\t", "")
            if mojimoji.zen_to_han(text) == mojimoji.zen_to_han(before_text):
                imId += 1
                y = x
                continue
            if state == 0:
                if text == "":
                    imId += 1
                    y = x
                    before_text = text
                    continue
                state = 1
                y = x
                series = pd.Series([imId, imId*0.5, text, 1],
                                   index=df.columns)
                df = df.append(series, ignore_index=True)
                before_text = text
            else:
                state = 1
                series = pd.Series([imId-1, (imId-1)*0.5, before_text, -1],
                                   index=df.columns)
                df = df.append(series, ignore_index=True)
                y = x
                before_text = text
                if text:
                    series = pd.Series([imId, imId*0.5, text, 1],
                                       index=df.columns)
                    df = df.append(series, ignore_index=True)
        y = x
        imId += 1
    df.to_csv("data/"+dirpath+".csv")
    pbar.close()
    print(cnt)

if __name__ == "__main__":
    find_devide_point(0, 10000)

