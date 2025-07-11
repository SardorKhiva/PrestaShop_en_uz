import os
import re
import xml.etree.ElementTree as ET
import requests

# --- Транслитерация латиница → кириллица ---
def latin_to_cyrillic(text):
    # Порядок важен: сначала длинные сочетания
    table = [
        ("sh", "ш"), ("ch", "ч"), ("ya", "я"), ("yu", "ю"), ("yo", "ё"), ("o‘", "ў"), ("g‘", "ғ"),
        ("Sh", "Ш"), ("Ch", "Ч"), ("Ya", "Я"), ("Yu", "Ю"), ("Yo", "Ё"), ("O‘", "Ў"), ("G‘", "Ғ"),
        ("a", "а"), ("b", "б"), ("d", "д"), ("e", "э"), ("f", "ф"), ("g", "г"), ("h", "ҳ"),
        ("i", "и"), ("j", "ж"), ("k", "к"), ("l", "л"), ("m", "м"), ("n", "н"), ("o", "о"),
        ("p", "п"), ("q", "қ"), ("r", "р"), ("s", "с"), ("t", "т"), ("u", "у"), ("v", "в"),
        ("x", "х"), ("y", "й"), ("z", "з"), ("A", "А"), ("B", "Б"), ("D", "Д"), ("E", "Э"),
        ("F", "Ф"), ("G", "Г"), ("H", "Ҳ"), ("I", "И"), ("J", "Ж"), ("K", "К"), ("L", "Л"),
        ("M", "М"), ("N", "Н"), ("O", "О"), ("P", "П"), ("Q", "Қ"), ("R", "Р"), ("S", "С"),
        ("T", "Т"), ("U", "У"), ("V", "В"), ("X", "Х"), ("Y", "Й"), ("Z", "З"),
        ("'", "ъ"), ("ʼ", "ъ"), ("’", "ъ"),
    ]
    for lat, cyr in table:
        text = text.replace(lat, cyr)
    return text

# --- Проверка на кириллицу ---
def is_cyrillic(text):
    return bool(re.search('[\u0400-\u04FF]', text))

def is_latin(text):
    return bool(re.search('[a-zA-Z]', text))

# --- Перевод через Google Translate (неофициально) ---
def translate_text(text, target_lang="uz"):
    if not text.strip():
        return text
    url = "https://translate.googleapis.com/translate_a/single"
    params = {
        'client': 'gtx',
        'sl': 'en',
        'tl': target_lang,
        'dt': 't',
        'q': text,
    }
    try:
        r = requests.get(url, params=params)
        r.raise_for_status()
        result = r.json()[0][0][0]
        return result
    except Exception as e:
        print(f"Ошибка перевода '{text}': {e}")
        return text

# --- Обработка одного XLIFF-файла ---
def process_xliff_file(filepath):
    ET.register_namespace('', "urn:oasis:names:tc:xliff:document:1.2")
    tree = ET.parse(filepath)
    root = tree.getroot()
    ns = {'ns': root.tag.split('}')[0].strip('{')}
    file_elem = root.find('.//ns:file', ns)
    if file_elem is not None:
        target_lang = file_elem.get('target-language', '')
        if target_lang == 'uz-Cyrl':
            # Проверяем, все ли <target> на кириллице
            all_cyrillic = True
            for tu in root.findall('.//ns:trans-unit', ns):
                tgt = tu.find('ns:target', ns)
                if tgt is not None and tgt.text and not is_cyrillic(tgt.text):
                    all_cyrillic = False
                    break
            if all_cyrillic:
                print(f"Пропущен (уже кириллица): {filepath}")
                return
        # Меняем язык на кириллицу
        file_elem.set('target-language', 'uz-Cyrl')
    changed = False
    for tu in root.findall('.//ns:trans-unit', ns):
        src = tu.find('ns:source', ns)
        tgt = tu.find('ns:target', ns)
        if tgt is not None and tgt.text:
            if is_cyrillic(tgt.text):
                continue  # Уже кириллица
            if is_latin(tgt.text):
                tgt.text = latin_to_cyrillic(tgt.text)
                changed = True
        else:
            # Перевести source, транслитерировать, записать
            if src is not None and src.text:
                uz_lat = translate_text(src.text, target_lang="uz")
                uz_cyrl = latin_to_cyrillic(uz_lat)
                if tgt is None:
                    tgt = ET.SubElement(tu, 'target')
                tgt.text = uz_cyrl
                tgt.set('state', 'final')
                changed = True
    if changed:
        tree.write(filepath, encoding='utf-8', xml_declaration=True)
        print(f"Обновлён: {filepath}")
    else:
        print(f"Без изменений: {filepath}")

# --- Обход всех файлов ---
def process_all_xliff_files(folder):
    for root_dir, _, files in os.walk(folder):
        for fname in files:
            if fname.endswith('.xlf') or fname.endswith('.xliff'):
                process_xliff_file(os.path.join(root_dir, fname))

if __name__ == "__main__":
    process_all_xliff_files("uz-UZ")
    print("Готово!")