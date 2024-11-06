import asyncio
import base64
import os
from typing import Tuple

import cv2
import numpy as np
from paddleocr import PaddleOCR

current_dir = os.path.abspath(os.path.dirname(__file__))

rec_model_path = os.path.join(current_dir, 'en_PP-OCRv4_rec_infer')
if os.name == 'posix':  # Linux 和 macOS 使用 posix
    rec_model_path = os.path.join(current_dir, 'en_PP-OCRv3_rec_infer')  # 识别模型文件夹路径

ocr = PaddleOCR(rec_model_dir=rec_model_path, lang='en', use_angle_cls=False, show_log=False)


class LocalModelImageSolver:

    async def solve(self, imgBase: str) -> Tuple[str, bool]:
        image_data = base64.b64decode(imgBase)
        image_array = np.frombuffer(image_data, np.uint8)
        image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
        # cv2.waitKey(0)
        _, binary_image_img = cv2.threshold(image, 150, 255, cv2.THRESH_BINARY_INV)
        kernel_img = np.ones((2, 2), np.uint8)
        opening_img = cv2.morphologyEx(binary_image_img, cv2.MORPH_ERODE, kernel_img)
        success, image_data = cv2.imencode('.png', opening_img)
        image_data = image_data.tobytes()
        results = await asyncio.to_thread(ocr.ocr, image_data, False, True, False)
        line_text, confidence = results[0][0]
        capcode = line_text.replace(" ", "")
        return (capcode, True)
