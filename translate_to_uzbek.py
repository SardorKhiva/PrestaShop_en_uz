#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
import xml.etree.ElementTree as ET
from pathlib import Path
import requests
import time

def translate_text(text, target_lang="uz"):
    """
    Простая функция перевода с использованием Google Translate API
    В реальном проекте лучше использовать официальный API с ключом
    """
    if not text or text.strip() == "":
        return text
    
    # Пропускаем технические строки, которые не нужно переводить
    if re.match(r'^[%s\d\s\-_\.]+$', text):
        return text
    
    # Пропускаем IP адреса, коды и технические идентификаторы
    if re.match(r'^\d+\.\d+\.\d+\.\d+$', text) or \
       re.match(r'^[A-Z]{2,3}$', text) or \
       re.match(r'^[a-zA-Z]{1,3}$', text):
        return text
    
    try:
        # Используем простой HTTP запрос к Google Translate
        # В продакшене лучше использовать официальный API
        url = "https://translate.googleapis.com/translate_a/single"
        params = {
            'client': 'gtx',
            'sl': 'en',
            'tl': target_lang,
            'dt': 't',
            'q': text
        }
        
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            result = response.json()
            if result and result[0] and result[0][0]:
                translated = result[0][0][0]
                return translated
        
        return text
    except Exception as e:
        print(f"Ошибка перевода '{text}': {e}")
        return text

def process_xliff_file(input_file, output_file):
    """Обрабатывает XLIFF файл и переводит непереведенные строки"""
    
    # Создаем директорию для выходного файла если её нет
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    # Парсим XML
    tree = ET.parse(input_file)
    root = tree.getroot()
    
    # Определяем namespace
    ns = {'xliff': 'urn:oasis:names:tc:xliff:document:1.2'}
    
    # Изменяем target-language на uz
    file_elem = root.find('.//xliff:file', ns)
    if file_elem is not None:
        file_elem.set('target-language', 'uz')
    
    # Обрабатываем все trans-unit элементы
    trans_units = root.findall('.//xliff:trans-unit', ns)
    total_units = len(trans_units)
    translated_count = 0
    
    print(f"Обрабатываю {input_file} ({total_units} строк)")
    
    for i, unit in enumerate(trans_units):
        source_elem = unit.find('xliff:source', ns)
        target_elem = unit.find('xliff:target', ns)
        
        if source_elem is not None and target_elem is not None:
            source_text = source_elem.text or ""
            target_text = target_elem.text or ""
            
            # Если target пустой или совпадает с source, переводим
            if not target_text or target_text == source_text:
                translated_text = translate_text(source_text)
                if translated_text != source_text:
                    target_elem.text = translated_text
                    translated_count += 1
                    print(f"  [{i+1}/{total_units}] '{source_text}' -> '{translated_text}'")
                
                # Небольшая задержка чтобы не перегружать API
                time.sleep(0.1)
    
    # Сохраняем результат
    tree.write(output_file, encoding='utf-8', xml_declaration=True)
    print(f"Переведено {translated_count} строк из {total_units}")
    print(f"Сохранено в {output_file}\n")

def main():
    """Основная функция"""
    
    # Создаем папку uz-UZ если её нет
    output_dir = "uz-UZ"
    os.makedirs(output_dir, exist_ok=True)
    
    # Получаем список всех .xlf файлов
    xlf_files = [f for f in os.listdir('.') if f.endswith('.en-US.xlf')]
    
    print(f"Найдено {len(xlf_files)} файлов для перевода")
    
    for input_file in xlf_files:
        # Создаем имя выходного файла
        output_file = os.path.join(output_dir, input_file.replace('.en-US.xlf', '.uz-UZ.xlf'))
        
        # Проверяем, существует ли уже переведенный файл
        if os.path.exists(output_file):
            print(f"Файл {output_file} уже существует, пропускаю...")
            continue
        
        try:
            process_xliff_file(input_file, output_file)
        except Exception as e:
            print(f"Ошибка при обработке {input_file}: {e}")
            continue

if __name__ == "__main__":
    main()