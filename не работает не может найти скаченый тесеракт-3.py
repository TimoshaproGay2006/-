import pytesseract
from PIL import Image
import json
import os

def ocr_to_json(image_path):
    """
    Распознает текст с изображения, сохраняет его координаты и текст в JSON файл.

    Args:
        image_path (str): Путь к изображению.
    """
    try:
        # Проверка, существует ли файл
        if not os.path.exists(image_path):
            print(f"Error: Image file not found at '{image_path}'")
            return

        # Загрузка изображения
        img = Image.open(image_path)

        # Распознавание текста и получение данных
        data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)

        # Формирование структуры JSON
        json_data = []
        for i in range(len(data['text'])):
            if data['text'][i].strip(): # Пропускаем пустые строки
                bbox = {
                  'left': data['left'][i],
                  'top': data['top'][i],
                  'width': data['width'][i],
                  'height': data['height'][i]
                    }
                json_data.append({
                    'text': data['text'][i],
                    'bbox': bbox
                })

        # Создание JSON файла с именем image_path.json
        output_file = os.path.splitext(image_path)[0] + ".json"

        with open(output_file, "w", encoding="utf-8") as outfile:
            json.dump(json_data, outfile, indent=4, ensure_ascii=False)

        print(f"Результаты распознавания сохранены в: {output_file}")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    image_path = input("Введите путь к изображению: ")
    ocr_to_json(image_path)