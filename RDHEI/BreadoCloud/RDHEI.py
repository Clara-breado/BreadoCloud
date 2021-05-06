from skimage import data,io
import numpy as np
import hashlib
import imagehash
import math
import tool
import matplotlib.pyplot as plt

from scipy import misc

class RDHEI:
    IMG = None
    IMG_PATH = None
    SD = None
    K = None
    Ke = None
    height = None
    width = None
    s = None
    n = None
    n_row = None
    n_col = None
    R_channel = None
    R_EIMG = None
    K_R = None
    K_G = None
    K_B = None

    def __init__(self,IMG,SD,K):
        self.IMG = IMG
        self.SD = SD
        self.K = K
        self.height = len(IMG)
        self.width = len(IMG[0])
        self.s = 2

##接口函数，生成加密图像
    def Encrypted(self):
        R = self.IMG[:, :, 0]
        self.R_channel = R
        G = self.IMG[:, :, 1]
        B = self.IMG[:, :, 2]
        [RIMG,self.K_R] = self.single_channel_Encrypted(R)
        [GIMG,self.K_G] = self.single_channel_Encrypted(G)
        [BING,self.K_B] = self.single_channel_Encrypted(B)

        self.R_EIMG = RIMG

        saveIMG = np.zeros((self.height, self.width, 3))
        saveIMG[:, :, 0] = RIMG
        saveIMG[:, :, 1] = GIMG
        saveIMG[:, :, 2] = BING
        saveIMG = saveIMG.astype('uint8')
        tool.get_qrKEY(self.K_R+self.K_G+self.K_B)
        io.imsave('encrypted.png', saveIMG)
        #io.imsave('qrKEY.png',qrKEY)
        io.imshow(saveIMG)
        plt.show()
        return  saveIMG

##接口函数，生成解密图像
    def Recovery(self,EIMG_PATH,KEY_PATH):
        EIMG = io.imread(EIMG_PATH)
        [K_R,K_G,K_B] = tool.read_qrKEY(KEY_PATH)
        RIMG = EIMG[:,:,0]
        GIMG = EIMG[:,:,1]
        BIMG = EIMG[:,:,2]
        ORIMG = self.single_channel_Recovery(RIMG,K_R)
        OGIMG = self.single_channel_Recovery(GIMG,K_G)
        OBING = self.single_channel_Recovery(BIMG,K_B)
        saveIMG = np.zeros((self.height, self.width, 3))
        saveIMG[:, :, 0] = ORIMG
        saveIMG[:, :, 1] = OGIMG
        saveIMG[:, :, 2] = OBING
        saveIMG = saveIMG.astype('uint8')
        io.imsave('Recovery.png', saveIMG)
        io.imshow(saveIMG)
        plt.show()

    def Embedded(self,sData):
        pass
    def Extracted(self,Ke):
        pass
    def single_channel_Embedded(self,sData):
        pass
    def single_channel_Extracted(self,Ke):
        pass
    def single_channel_Encrypted(self,sIMG):
        self.n = int((self.height*self.width)/(self.s*self.s))
        self.n_row = int(self.height/self.s)
        self.n_col = int(self.width/self.s)
        IMGBLK = RDHEI.blocking(self,sIMG)
        #HIMG = imagehash.dhash(IMGBLK)
        #HK = hash()
        #todo 裂开了，没找到对矩阵做哈希的api,能否调用在线的？
        Ke = tool.datahash(IMGBLK,self.K)
        self.Ke = Ke
        Ke256 = np.zeros((1,256))
        # Ke256[0:8] = tool.get_bit(Ke[0])
        # Ke256[8:16] = tool.get_bit(Ke[1])
        for i in range(32):
            Ke256[0,i*8:i*8+8] = tool.get_bit(Ke[i])

        #TSS
        X = np.zeros((self.n+1,1))
        U = np.zeros((2,1))
        R = np.zeros((self.n,1))
        V = np.zeros((2,1))

        for i in range(0,64):
            U[0] = U[0]+Ke256[0,i]*pow(2,63-i)
        for i in range(64,128):
            U[1] = U[1]+Ke256[0,i]*pow(2,127-i)

        for i in range(128,192):
            V[0] = V[0]+Ke256[0,i]*pow(2,191-i)
        for i in range(192,256):
            V[1] = V[1]+Ke256[0,i]*pow(2,255-i)

        x0 = U[0]/pow(2,90)
        r0 = U[1]/pow(2,90)
        X[0] = x0
        R[0] = r0

        for i in range(1,3):
            X[i] = ((X[i-1]*U[i-1]*V[i-1])/pow(2,80)+X[i-1])%1
            R[i] = ((R[i-1]*U[i-1]*V[i-1])/pow(2,80)+R[i-1])%4
        r = 4-R[2]
        X[0] = X[2]
        for i in range(self.n):
            if(X[i]<0.5):
                tmp = (r*X[i]/2 + ((4-r)*math.sin(3.1416*X[i])/4))%1
            else:
                tmp = (r*(1-X[i])/2 + ((4-r)*math.sin(3.1416*X[i])/4))%1
            tmp = tmp.astype(dtype='double')
            X[i+1] = tmp
            R[i] = math.floor((tmp*pow(2,40))%256)
            R[i] = R[i].astype(dtype='float')
        R = R.astype(dtype='float')
        R4 = np.zeros((self.s*self.s,len(R)))
        R4 = R4.astype(dtype='float')
        R4[0] = R.T
        R4[1] = R.T
        R4[2] = R.T
        R4[3] = R.T
        EIMG_BLK = (IMGBLK+R4)%256
        EIMG = self.unblocking(EIMG_BLK)

        EIMG = EIMG.astype('uint8')
        saveIMG = np.zeros((self.height,self.width,3))
        saveIMG[:,:,0] = EIMG
        saveIMG[:,:,1] = EIMG
        saveIMG[:,:,2] = EIMG
        saveIMG = saveIMG.astype('uint8')
        io.imsave('test.jpg',saveIMG)
        #io.imshow(saveIMG)
        #plt.show()
        return EIMG,Ke

    def single_channel_Recovery(self,sIMG,inputK):
        s_IMG = RDHEI.blocking(self,sIMG)
        Ke256 = np.zeros((1,256))
        for i in range(32):
            Ke256[0,i*8:i*8+8] = tool.get_bit(inputK[i])
        #TSS
        X = np.zeros((self.n + 1, 1))
        U = np.zeros((2, 1))
        R = np.zeros((self.n, 1))
        V = np.zeros((2, 1))
        for i in range(0, 64):
            U[0] = U[0] + Ke256[0, i] * pow(2, 63 - i)
        for i in range(64, 128):
            U[1] = U[1] + Ke256[0, i] * pow(2, 127 - i)
        for i in range(128, 192):
            V[0] = V[0] + Ke256[0, i] * pow(2, 191 - i)
        for i in range(192, 256):
            V[1] = V[1] + Ke256[0, i] * pow(2, 255 - i)

        x0 = U[0] / pow(2, 90)
        r0 = U[1] / pow(2, 90)
        X[0] = x0
        R[0] = r0

        for i in range(1, 3):
            X[i] = ((X[i - 1] * U[i - 1] * V[i - 1]) / pow(2, 80) + X[i - 1]) % 1
            R[i] = ((R[i - 1] * U[i - 1] * V[i - 1]) / pow(2, 80) + R[i - 1]) % 4
        r = 4 - R[2]
        X[0] = X[2]

        for i in range(self.n):
            if (X[i] < 0.5):
                X[i + 1] = (r * X[i] / 2 + ((4 - r) * math.sin(3.1416 * X[i]) / 4)) % 1
            else:
                X[i + 1] = (r * (1 - X[i]) / 2 + ((4 - r) * math.sin(3.1416 * X[i]) / 4)) % 1
            R[i] = math.floor((X[i + 1] * pow(2, 40)) % 256)
        R4 = np.zeros((self.s*self.s,len(R)))
        R4[0] = R.T
        R4[1] = R.T
        R4[2] = R.T
        R4[3] = R.T
        O_IMG = (s_IMG-R4)%256
        OIMG = self.unblocking(O_IMG)
        OIMG = OIMG.astype('uint8')
        # saveIMG = np.zeros((self.height, self.width, 3))
        # saveIMG[:, :, 0] = OIMG
        # # saveIMG[:, :, 1] = OIMG
        # # saveIMG[:, :, 2] = OIMG
        # saveIMG = saveIMG.astype('uint8')
        # io.imsave('test2.jpg', saveIMG)
        # io.imshow(saveIMG)
        # plt.show()
        return OIMG

    def blocking(self,sIMG):
        k=0
        BLK = np.zeros((self.n,self.s,self.s))

        for i in range(self.n_row):
            for j in range(self.n_col):
                BLK[k,:,:] = sIMG[i*self.s:i*self.s + self.s,
                             j*self.s:j*self.s + self.s]
                k = k+1
        BLK = BLK.reshape(-1,4) #auto -1
        BLK = BLK.T
        return BLK

    def unblocking(self,BLK):
        k = 0
        BLK = BLK.T.reshape(-1,2,2)
        EIMG = np.zeros((self.height,self.width))

        for i in range(self.n_row):
            for j in range(self.n_col):
                BLK[k,:,:] = BLK[k,:,:].T
                EIMG[i*self.s:i*self.s+self.s,
                    j*self.s:j*self.s+self.s] = BLK[k,:,:]
                k = k+1
        return EIMG
