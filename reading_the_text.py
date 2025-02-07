import pytesseract
from PIL import Image
import os
import json

def ocr_image_to_json(image_path):
    """
    Распознает текст на изображении, сохраняет координаты и текст в JSON файл.

    Args:
        image_path (str): Путь к изображению.
    """
    try:
        # Проверка, существует ли файл
        if not os.path.exists(image_path):
            print(f"Error: Image file not found at '{image_path}'")
            return

        # Настройка пути к tesseract
        pytesseract.pytesseract.tesseract_cmd = r'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'

        # Распознавание текста с указанием языков
        image = Image.open(image_path)
        data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT, lang='rus+eng')

        # Формирование JSON структуры
        json_data = []
        for i in range(len(data['text'])):
            if int(data['conf'][i]) > 0:  # убираем строки без текста
                json_data.append({
                    'text': data['text'][i],
                    'left': data['left'][i],
                    'top': data['top'][i],
                    'width': data['width'][i],
                    'height': data['height'][i],
                    'confidence': data['conf'][i]
                })

        # Определение имени JSON файла
        base_name = os.path.splitext(os.path.basename(image_path))[0]
        json_file_name = f'{base_name}.json'

        # Получение пути к папке, где находится скрипт
        script_dir = os.path.dirname(os.path.abspath(__file__))

        # Формирование полного пути к JSON файлу
        json_file_path = os.path.join(script_dir, json_file_name)

        # Запись JSON данных в файл
        with open(json_file_path, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, indent=4, ensure_ascii=False)

        print(f"JSON file created at: {json_file_path}")

    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    image_path = input("Введите путь к изображению: ")
    ocr_image_to_json(image_path)