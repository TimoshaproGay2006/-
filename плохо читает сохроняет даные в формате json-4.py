import easyocr
import os
import json

def ocr_image(image_path):
    """
    Распознает текст на изображении, сохраняет результаты в JSON файл.

    Args:
        image_path (str): Путь к изображению.
    """
    try:
        # Проверка, существует ли файл
        if not os.path.exists(image_path):
            print(f"Error: Image file not found at '{image_path}'")
            return None

        # Инициализация EasyOCR (с языками, если нужно)
        reader = easyocr.Reader(['ru', 'en'])  # ['ru', 'en'] - русский и английский
        # Распознавание текста
        results = reader.readtext(image_path)

        # Формирование структуры данных для JSON
        extracted_data = []
        for (bbox, text, prob) in results:
            (tl, tr, br, bl) = bbox
            extracted_data.append({
                "text": text,
                "confidence": prob,
                "coordinates": {
                    "top_left": [int(tl[0]), int(tl[1])],
                    "top_right": [int(tr[0]), int(tr[1])],
                    "bottom_right": [int(br[0]), int(br[1])],
                    "bottom_left": [int(bl[0]), int(bl[1])]
                }
            })
        return extracted_data

    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def save_to_json(data, output_path):
    """Сохраняет данные в JSON файл."""
    try:
        with open(output_path, "w", encoding="utf-8") as json_file:
            json.dump(data, json_file, ensure_ascii=False, indent=4)
        print(f"Данные успешно сохранены в: {output_path}")
    except Exception as e:
         print(f"Ошибка при сохранении в JSON: {e}")


if __name__ == "__main__":
    image_path = input("Введите путь к изображению: ")

    # Получаем данные
    extracted_data = ocr_image(image_path)

    if extracted_data:
        # Создаем имя для файла JSON
        base_name = os.path.splitext(os.path.basename(image_path))[0]
        json_file_name = f"{base_name}.json"
        output_json_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), json_file_name)

        # Сохраняем данные в JSON
        save_to_json(extracted_data, output_json_path)