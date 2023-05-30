import os
import time
import fnmatch
from exif import Image
from pymediainfo import MediaInfo
from datetime import datetime
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
        Функция переводит время UTC в местное (доработать!!!)
    """
    utc_datetime = utc_datetime.replace('UTC ', '')
    utc_date = utc_datetime.split(' ')[0].split('-')
    utc_time = utc_datetime.split(' ')[1].split(':')
    local_date = utc_date[2] + '-' + utc_date[1] + '-' + utc_date[0]

    local_hour_int = int(utc_time[0]) + 8
    if local_hour_int >= 24:
        local_hour_int = local_hour_int - 24
        if local_hour_int < 10:
            local_hour = '0' + str(local_hour_int)
    else:
        local_hour = str(local_hour_int)

    local_time = local_hour + '.' + utc_time[1] + '.' + utc_time[2]
    local_datetime = local_date + ' ' + local_time
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

                                check_date = encoded_date.split(' ')
                                check_hour = check_date[1].split('.')

                                if len(check_hour[0]) == 1:
                                    check_hour[0] = '0' + check_hour[0]
                                    check_time = check_hour[0] + '.' + \
                                        check_hour[1] + '.' + check_hour[2]
                                    check_date[1] = check_time
                                    encoded_date = check_date[0] + ' ' + check_date[1]

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
                                            get_datetime = my_image.get(
                                                "datetime").split(' ')
                                            year = get_datetime[0].split(':')[0]
                                            month = get_datetime[0].split(':')[1]
                                            day = get_datetime[0].split(':')[2]
                                            norm_date = day + '-' + month + '-' + year
                                            file_time = norm_date + ' ' + \
                                                get_datetime[1].replace(':', '.')
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
