import easyocr
import os

def ocr_image(image_path):
    """
    Распознает текст на изображении и выводит его в консоль.

    Args:
        image_path (str): Путь к изображению.
    """
    try:
        # Проверка, существует ли файл
        if not os.path.exists(image_path):
            print(f"Error: Image file not found at '{image_path}'")
            return

        # Инициализация EasyOCR (с языками, если нужно)
        reader = easyocr.Reader(['ru', 'en'])  # ['ru', 'en'] - русский и английский
        # Распознавание текста
        results = reader.readtext(image_path)

        # Вывод результатов в консоль
        for (bbox, text, prob) in results:
            print(f"Текст: {text}, Уверенность: {prob}")
            (tl, tr, br, bl) = bbox
            print(f"Координаты: [{int(tl[0])}, {int(tl[1])}], [{int(tr[0])}, {int(tr[1])}], [{int(br[0])}, {int(br[1])}], [{int(bl[0])}, {int(bl[1])}]")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    image_path = input("Введите путь к изображению: ")
    ocr_image(image_path)