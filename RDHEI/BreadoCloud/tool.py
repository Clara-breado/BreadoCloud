import hashlib
import skimage
import math
from skimage import io
import matplotlib.pyplot as plt

import hashlib
import numpy as np
def preprocess(SRC_path):
    SRC = io.imread(SRC_path)
    R = SRC[:,:,0]
    G = SRC[:,:,1]
    B = SRC[:,:,2]
    return SRC
def datahash(data1,data2):
    HIMG = get_uint8("5d22edc81b6bf20098efff650e371019")
    HK = get_uint8("8298c03ef129e6678c7d853cb01b094d")
    return list_xor(HIMG,HK)

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