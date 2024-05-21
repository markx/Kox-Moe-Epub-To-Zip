# -*- coding: utf-8 -*-

"""
@author: dean
@software: PyCharm
@file: epub_to_zip.py
@time: 2023/2/6 23:22
"""
import os
import sys
import time
import shutil
import zipfile
from ebooklib import epub
from lxml import etree


class Converter:
    def __init__(self, file_path, target_path):
        self.file_path = file_path
        self.target_path = target_path

    def get_epub_title(self):
        book = epub.read_epub(self.file_path)
        title = book.get_metadata('DC', 'title')[0][0]
        book_path = str(self.target_path + os.sep + title)
        return book_path, title

    def extract_img_from_epub(self):
        extract_path = self.get_epub_title()[0]
        # prepare to read from .epub file
        with zipfile.ZipFile(self.file_path, mode='r') as _zip:
            # 读取html文件
            for _name in _zip.namelist():
                if _name[-5:] == '.html':
                    text = _zip.read(_name)
                    xml = etree.HTML(text)
                    # 读取 img 对应的图片路径
                    img_path = xml.xpath('//img/@src')[0][3:]
                    img_ext = xml.xpath('//img/@src')[0][-4:]
                    # 读取页码信息
                    page_info = xml.xpath('/html/head/title/text()')[0]

                    if "image/cover" in img_path:
                        continue
                    if "image/createby" in img_path:
                        continue

                    if img_ext in set(['.jpg', '.png']):
                        try:
                            # 解压缩图片
                            _zip.extract(img_path, extract_path)
                            # 按编号顺序改名
                            os.rename(extract_path + '/' + img_path, extract_path + '/' + page_info + img_ext)
                        except Exception as e:
                            print(e)

                    elif '.' not in img_ext:
                        pass
                    else:
                        print('不支持的图片格式！！')
            # 删除已经为空的image文件夹
            shutil.rmtree(extract_path + '/' + 'image')

    def zip_images(self):
        book_path, title = self.get_epub_title()
        filelist = os.listdir(book_path)
        _zip = zipfile.ZipFile(book_path + '.zip', 'w', zipfile.ZIP_DEFLATED)
        for file in filelist:
            file_full_path = os.path.join(book_path, file)
            # file_full_path是文件的全路径，file是文件名，这样压缩时不会带多层目录
            _zip.write(file_full_path, file)
        _zip.close()
        # shutil.rmtree(book_path)
        print(title + '.zip  创建成功！')
        return title

def get_time():
    current_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    return current_time


def main():

    epub_path, output_path = sys.argv[1:3]
    print(epub_path, "->", output_path)
    if epub_path == '' or output_path == '':
        return False

    start_time = time.time()
    # 开始转换程序
    epub_names = os.listdir(epub_path)
    for epub_name in epub_names:
        try:
            root, _ext = os.path.splitext(epub_path + os.sep + epub_name)
            if _ext == '.epub':
                file_dir = root + _ext
                trans = Converter(file_dir, output_path)
                target_path, _ = trans.get_epub_title()
                if os.path.exists(target_path + ".zip"):
                    print(target_path + " already exists, skip " + epub_name)
                    continue
                print("start converting ", target_path)
                trans.extract_img_from_epub()
                success_title = trans.zip_images()
                print(success_title)
        except Exception as e:
            print(e)

        # 显示转换用时
        finish_time = time.time()
        time_used = "{:.2f}".format(finish_time - start_time)
        print("used time: ", time_used)

if __name__ == '__main__':
    main()
