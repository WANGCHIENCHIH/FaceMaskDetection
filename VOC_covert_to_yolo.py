# -*- coding: utf-8 -*-
"""
@author: jameswang
"""

import os
import shutil
from bs4 import BeautifulSoup
from math import floor

def run_convert(all_classes, image_folder, xml_folder, target_folder, write_txt):
    """

    Parameters
    ----------
    all_classes : dict
        label格式 {"label":"index"}
    image_folder : str
        img資料夾路徑
    xml_folder : str
        xml資料夾路徑.
    target_folder : str
        img copy資料夾路徑.
    write_txt : str
        轉換後的txt存放路徑.

    Returns
    -------
    None.

    """
    #now_path = os.getcwd()
    data_counter = 0

    for data_file in os.listdir(xml_folder):
        # listdir()讀取 指定資料夾下所有的資料夾與文件
        try:
            #for windows
            xml_tmp_path=xml_folder+data_file
            with open(xml_tmp_path, 'r') as f:
                print("read file...")
                # 讀取單一xml
                soup = BeautifulSoup(f.read(), 'xml')
                # 這張圖片的名稱
                img_name = data_file.replace('xml','jpg')#soup.select_one('filename').text
                # 這張圖片的長寬'
                for size in soup.select('size'):
                    img_w = int(size.select_one('width').text)
                    img_h = int(size.select_one('height').text)
                # 一張圖會有0-n個label，建立一個list來存object   
                img_info = []
                # 有n個obj
                for obj in soup.select('object'):
                    xmin = int(obj.select_one('xmin').text)
                    xmax = int(obj.select_one('xmax').text)
                    ymin = int(obj.select_one('ymin').text)
                    ymax = int(obj.select_one('ymax').text)
                    objclass = all_classes.get(obj.select_one('name').text)
                    # 轉換成yolo，依照公式
                    x = (xmin + (xmax-xmin)/2) * 1.0 / img_w
                    y = (ymin + (ymax-ymin)/2) * 1.0 / img_h
                    w = (xmax-xmin) * 1.0 / img_w
                    h = (ymax-ymin) * 1.0 / img_h
                    img_info.append(' '.join([str(objclass), str(x),str(y),str(w),str(h)]))

                # copy image to yolo path and rename
                img_path = image_folder+ img_name
                img_format = img_name.split('.')[1]  # jpg or png
                shutil.copyfile(img_path, target_folder + str(data_counter) + '.' + img_format)
                
                # create yolo bndbox txt
                with open(target_folder + str(data_counter) + '.txt', 'a+') as f:
                    f.write('\n'.join(img_info))

                # txt路徑寫入
                with open(write_txt, 'a') as f:
                    #path = os.path.join(now_path, target_folder)
                    path = target_folder
                    line_txt = [path + str(data_counter) + '.' + img_format, '\n']
                    f.writelines(line_txt)

                data_counter += 1
                    
        except Exception as e:
            print(e)
           
    print('the file is processed')




all_classes = dict()#{'none': 2, 'bad': 1, 'good': 0}
image_folder = "Dataset_for_Mask_Wearing/images/"
xml_folder = "Dataset_for_Mask_Wearing/labels/"
target_folder = "Dataset_for_Mask_Wearing/datas/"
write_txt = 'Dataset_for_Mask_Wearing/cfg/labels.txt'
class_path = "Dataset_for_Mask_Wearing/cfg/class.names"
cfg_path='Dataset_for_Mask_Wearing/cfg/'
# read class
with open(class_path, 'r') as f:
    classes=f.read().split("\n")
    for index,element in enumerate(classes):
        all_classes[element]=index
    

# 如果目標資料夾未建立，建立新資料夾
if not os.path.exists(target_folder):
    os.mkdir(target_folder)
else:
    # 如果目標資料夾內有東西，清空
    lsdir = os.listdir(target_folder)
    for name in lsdir:
        if name.endswith('.txt') or name.endswith('.jpg') or name.endswith('.png'):
            os.remove(target_folder+ name)

# 如果存txt的cfg資料夾未建立，建立cfg資料夾
#cfg_file = write_txt.split('/')[0]
#if not os.path.exists(cfg_file):
#    os.mkdir(cfg_file)
# 建立空的txt檔
if os.path.exists(write_txt):
    file=open(write_txt, 'w')

run_convert(all_classes, image_folder, xml_folder, target_folder, write_txt)



# divided data
# between 0.5-1
train_percent=0.8
datasets = [(target_folder+ f) for f in os.listdir(target_folder) if not f.endswith('.txt')]

end_train=floor(len(datasets)*train_percent)

train_set=datasets[:end_train]
test_set=datasets[end_train:]

with open(cfg_path+'train.txt', 'w') as f:
    f.write('\n'.join(train_set))
    
with open(cfg_path+'test.txt', 'w') as f:
    f.write('\n'.join(test_set))
