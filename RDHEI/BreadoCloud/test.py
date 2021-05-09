from RDHEI import RDHEI
from tool import preprocess
from tool import datahash
import tool
import numpy as np
from skimage import io
if __name__ == "__main__":
    #process img
    IMG_PATH = 'G:\\python\\BreadoCloud\\'
    KEY_PATH = 'G:\\python\\BreadoCloud\\src_qrKEY.png'

    NAME_SRC = 'src.jpg'
    NAME_EN = 'src_en.png'
    NAME_EM = 'src_en_em.png'
    SD = 'breadocloudembed'
    p = RDHEI(IMG_PATH)
    test = p.Encrypted(NAME_SRC,k='2018srtp')
    o = p.Recovery(NAME_EN,KEY_PATH)
    EM = p.Embedded(NAME_EN,SD) 
    sd = p.Extracted(NAME_EM,'000')
    print(sd)