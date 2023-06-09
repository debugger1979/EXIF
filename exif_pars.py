import os
import time
import fnmatch
from exif import Image
from pymediainfo import MediaInfo
from datetime import datetime, timezone
import mimetypes
import sys


def new_filename(filename):
    """
        Функция проверяет наличие уже существующего файла и, при наличии, добавляет к имени (n).
        Возвращает новое имя файла.
    """
    n = 0
    result = filename
    while os.path.exists(result):
        split_name = os.path.splitext(filename)
        ext = split_name[1]
        name = split_name[0]

        if name.find('(') != -1 and name.find(')') != -1:
            n = int(name.split('(')[1].split(')')[0])
            name = name.replace('(' + str(n) + ')', '')
        n += 1
        result = name + '(' + str(n) + ')' + ext

    return result


def get_time_file(name):
    """
        Функция определения времени (создания/изменения) файла в ОС.
        Сравнивает время создания и изменения файла, возвращает наименьшее значение.
    """
    ctime_ = os.path.getctime(name)
    mtime_ = os.path.getmtime(name)

    ctime_file = time.gmtime(ctime_)
    mtime_file = time.gmtime(mtime_)

    if ctime_ > mtime_:
        return time.strftime("%d-%m-%Y", mtime_file) + ' ' + time.ctime(mtime_).split(' ')[-2].replace(':', '.')
    else:
        return time.strftime("%d-%m-%Y", ctime_file) + ' ' + time.ctime(ctime_).split(' ')[-2].replace(':', '.')


def utc_to_local(utc_datetime):
    """
        Функция переводит время UTC в местное
    """
    local_datetime = datetime.strptime(utc_datetime, '%Y-%m-%d %H:%M:%S %Z').replace(tzinfo=timezone.utc).astimezone(tz=None).strftime('%d-%m-%Y %H:%M:%S')
    return local_datetime


# путь к папке или файлу задается в параметрах коммандной строки
# Формат:
# python exif_pars.py <путь>

if len(sys.argv) == 2:
    img_path = sys.argv[1]
    
    if os.path.exists(img_path):
        
        for roots, dirs, files in os.walk(img_path):
            for file in files:
                full_name = os.path.join(roots, file)
                if fnmatch.fnmatch(full_name, '*.*'): 
                    
                    # Отфильтровываем файлы изображений и видео
                    try:
                        mime_type = mimetypes.guess_type(full_name)[0].split('/')[0]
                    except:
                        mime_type = 'None'

                    if mime_type in ('video', 'image'):

                        # Внимание! Перед использованием скрипта, необходимо скачать пакет MediaInfo и разместить библиотеку MediaInfo.dll
                        # в папке скрипта и указать путь в модуле MwdiaInfo.
                        media_can_parse = MediaInfo.can_parse(
                            'MediaInfo.dll')
                        media_parse = MediaInfo.parse(filename=full_name)

                        for i in media_parse.tracks:
                            img_meta = i.to_data()
                            
                            if i.track_type == 'Video':

                                if 'encoded_date' in img_meta:
                                    encoded_date = utc_to_local(
                                        img_meta['encoded_date'])

                                elif 'file_last_modification_date' in img_meta:
                                    

                                    encoded_date = utc_to_local(
                                        img_meta['file_last_modification_date'])
                                else:
                                    encoded_date = get_time_file(full_name)

                                file_time = encoded_date

                            elif i.track_type == 'Image':
                                try:
                                    with open(full_name, 'rb') as image_file:
                                        my_image = Image(image_file)
                                except:
                                    # мы не смогли открыть файл как изображение
                                    file_time = get_time_file(full_name)

                                else:
                                    if my_image.has_exif:
                                        # у файла есть EXIF
                                        try:
                                            get_datetime = my_image.get("datetime")
                                            file_time = datetime.strptime(UTC_datetime, '%Y:%m:%d %H:%M:%S').strftime('%Y-%m-%d %H:%M:%S')
                                        except:
                                            file_time = get_time_file(full_name)
                                        finally:
                                            pass
                                    else:
                                        file_time = get_time_file(full_name)

                        new_name = full_name.replace(os.path.basename(
                            full_name), '') + file_time + os.path.splitext(full_name)[1]

                        try:
                            os.rename(full_name, new_name)
                        except FileExistsError:
                            os.rename(full_name, new_filename(new_name))
                            print(full_name + '   ------->    ' +
                                new_filename(new_name))
                        else:
                            print(full_name + '   ------->    ' + new_name)

                        file_time = ''
    else:
        print('Ошибка! Указан неверный путь к медиафайлу или папке с медиафайлами!')
else:
    print('Ошибка! Не указан путь к медиафайлу или папке с медиафайлами!')
