"""
Модуль сохранения данных о товарах в Excel.
Импортирует генератор one_card() из parser.py, собирает данные
и записывает их в таблицу .xlsx с валютным форматированием.
"""

import os
import xlsxwriter
from parser import one_card


# Куда сохраняем файл и как называем колонки
OUT_FILE = r"E:\site_to_excel\products.xlsx"
HEADERS = ["Название", "Цена", "Описание", "Картинка", "Категория", "Наличие"]


def _price(value):
    """Приводит цену к float. Возвращает None, если это не число."""
    try:
        return float(str(value).replace(",", "."))
    except (TypeError, ValueError):
        return None


def save_to_excel(rows, path=OUT_FILE):
    """
    Записывает данные из итератора rows в Excel-файл.

    Args:
        rows: итератор кортежей (название, цена, описание, картинка, категория, наличие).
        path: путь к сохраняемому файлу (по умолчанию OUT_FILE).
    """
    # Создаем папку для файла, если ее еще нет
    os.makedirs(os.path.dirname(path), exist_ok=True)

    workbook = xlsxwriter.Workbook(path)
    sheet = workbook.add_worksheet()

    # Формат: пишем число, отображаем как доллары с двумя знаками после запятой
    money = workbook.add_format({"num_format": "$#,##0.00"})

    # Записываем шапку таблицы
    sheet.write_row(0, 0, HEADERS)

    # Идем по данным, начиная со второй строки (start=1)
    for i, (name, price, info, img, cate, inventory) in enumerate(rows, start=1):
        sheet.write(i, 0, name)

        # Пытаемся записать цену как число (чтобы работали формулы и сортировка)
        num = _price(price)
        if num is None:
            # Если пришла строка (например, "Нет ключа price") — пишем как текст
            sheet.write(i, 1, price)
        else:
            sheet.write_number(i, 1, num, money)

        # Остальные поля (описание, картинка, категория, наличие) пишем одной строкой
        sheet.write_row(i, 2, [info, img, cate, inventory])

    workbook.close()
    print(f"Файл сохранён: {path}")


if __name__ == "__main__":
    save_to_excel(one_card())
