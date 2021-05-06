import hashlib
import skimage
import math
from skimage import io
import matplotlib.pyplot as plt
import qrcode
from PIL import Image
from pyzbar import pyzbar

import hashlib
import numpy as np
def preprocess(SRC_path):
    SRC = io.imread(SRC_path)
    R = SRC[:,:,0]
    G = SRC[:,:,1]
    B = SRC[:,:,2]
    return SRC
def datahash(data1,data2):
    type(data1)
    data1_str = str(data1)
    data2_str = str(data2)
    m1 = hashlib.md5()
    m2 = hashlib.md5()
    m1.update(data1_str.encode("utf-8"))
    m2.update(data2_str.encode("utf-8"))
    h1 = get_uint8(m1.hexdigest())
    h2 = get_uint8(m2.hexdigest())
    #HIMG = get_uint8("83d8696c5441827f6e60b8ed1b0e1262")
    #HK = get_uint8("30c98532a7034f0c908086eec86afccb")
    return list_xor(h1,h2)

def get_uint8(str):
    res = []
    for c in str:
        res.append(ord(c))
    return res

def get_uint8_matrix(M):
    ans = np.zeros((len(M),len(M[0])))
    for i in range(len(M)):
        for j in range(len(M[0])):
            ans[i][j] = math.floor(M[i][j])
    return ans

def list_xor(list1,list2):
    res = []
    for i in range(len(list1)):
        res.append(list1[i]^list2[i])
    return res

def get_bit(dec):
    bits = np.zeros((1,8))
    for i in range(8):
        bits[0][i] = dec%2
        dec = int(dec/2)
    return bits

def get_qrKEY(str_key):
    qr = qrcode.QRCode()
    qr.add_data(str_key)
    qrKEY = qr.make_image(fill_color='blue', back_color='pink')
    qrKEY.save("qrKEY.png")

def read_qrKEY(qr_path):
    qrIMG = Image.open(qr_path)
    F = pyzbar.decode(qrIMG)
    Ke = pyzbar.decode(qrIMG)[0].data.decode("utf-8")
    Ke = Ke.split("[")[1].split("]")[0]
    Kelist = Ke.split(",")
    Kelist = list(map(int, Kelist))
    K_R = Kelist[0:32]
    K_G = Kelist[32:64]
    K_B = Kelist[64:128]
    #K_R,K_G,K_B type = list
    return [K_R,K_G,K_B]