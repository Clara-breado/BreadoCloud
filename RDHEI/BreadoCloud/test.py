from RDHEI import RDHEI
from tool import preprocess
from tool import datahash
import tool
import numpy as np
from skimage import io
if __name__ == "__main__":
    #process img
    IMG_PATH = 'G:\gradethree\RDHEI\src_img\src.jpg'
    EIMG_PATH = 'G:\python\BreadoCloud\encrypted.png'
    EMIMG_PATH = 'G:\python\BreadoCloud\EMBED.png'
    KEY_PATH = 'G:\python\BreadoCloud\qrkey.png'
    SRC_IMG = preprocess(IMG_PATH)

    SRC = np.array([[2, 7, 4, 2],
                     [35, 9, 1, 5],
                     [22, 12, 3, 2],
                     [15, 16, 8, 100]])
    t1 = np.zeros((1,8))
    t2 = np.zeros((1,16))
    a = tool.get_uint8("5deg")
    t1 = tool.get_bit(13)
    t2[0,0:8] = tool.get_bit(35)
    t3 = pow(2,3)
    Matrix = np.array([[1.65, 2.888, 3894.5],
                       [3, 2, 1],
                       [4, 5.4864, 6]])
    b = tool.get_uint8_matrix(Matrix)
    p = RDHEI(IMG=SRC_IMG, SD='breadocloud_embed', K='2018srtp')#todo path/NAME/
    test = p.Encrypted() #todo PATH+QRKEY_NAME input：K,SRC_IMG,KEY_IMG 只有加密后的存路径 其他存图片
    o = p.Recovery(EIMG_PATH,KEY_PATH) #todo input:KEY_IMG output:OIMG
    EM = p.Embedded(EIMG_PATH,'breadocloudembed') #todo input:SD output:EMIMG_PATH,QRKEY2_PATH-------EXTRACTED input:QRKEY2_PATH,EMIMG_PATH OUTPUT:SD
    sd = p.Extracted(EMIMG_PATH,'000')
    print(sd)