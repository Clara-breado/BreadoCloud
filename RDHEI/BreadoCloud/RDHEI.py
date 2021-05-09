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
    IMG_NAME = None
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

    def __init__(self,IMG_PATH):
        self.IMG_PATH = IMG_PATH
        self.s = 2

##接口函数，生成加密图像
    def Encrypted(self,FILE_NAME,k):
        self.IMG_NAME = FILE_NAME.split('.',-1)[0]
        IMG = self.preprocess(self.IMG_PATH+FILE_NAME)
        R = IMG[:, :, 0]
        G = IMG[:, :, 1]
        B = IMG[:, :, 2]
        [RIMG,self.K_R] = self.single_channel_Encrypted(R,k)
        [GIMG,self.K_G] = self.single_channel_Encrypted(G,k)
        [BING,self.K_B] = self.single_channel_Encrypted(B,k)

        saveIMG = np.zeros((self.height, self.width, 3))
        saveIMG[:, :, 0] = RIMG
        saveIMG[:, :, 1] = GIMG
        saveIMG[:, :, 2] = BING
        saveIMG = saveIMG.astype('uint8')
        savePath = self.IMG_PATH + self.IMG_NAME
        tool.get_qrKEY(self.K_R+self.K_G+self.K_B,savePath)
        savePath += '_en.png'   # encrypted
        io.imsave(savePath, saveIMG)
        io.imshow(saveIMG)
        plt.show()
        return savePath

##接口函数，生成解密图像
    def Recovery(self,FILE_NAME,KEY_PATH):
        #EIMG = io.imread(EIMG_PATH)
        self.IMG_NAME = FILE_NAME.split('.', -1)[0]
        EIMG = self.preprocess(self.IMG_PATH + FILE_NAME)
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
        savePath = self.IMG_PATH + self.IMG_NAME+'_re.png'  # Recovery IMG

        io.imsave(savePath, saveIMG)
        io.imshow(saveIMG)
        plt.show()
        return savePath

##接口函数，隐藏信息
    def Embedded(self,FILE_NAME,sData):
        # IMG = io.imread(EIMG_PATH)
        self.IMG_NAME = FILE_NAME.split('.', -1)[0]
        EIMG = self.preprocess(self.IMG_PATH + FILE_NAME)
        RIMG = EIMG[:,:,0]
        GIMG = EIMG[:,:,1]
        BIMG = EIMG[:,:,2]
        [R_D,G_D,B_D] = tool.dataSplit(sData)
        EmRIMG = self.single_channel_Embedded(RIMG,R_D)
        EmGIMG = self.single_channel_Embedded(GIMG,G_D)
        EmBIMG = self.single_channel_Embedded(BIMG,B_D)

        saveIMG = np.zeros((self.height, self.width, 3))
        saveIMG[:, :, 0] = EmRIMG
        saveIMG[:, :, 1] = EmGIMG
        saveIMG[:, :, 2] = EmBIMG
        saveIMG = saveIMG.astype('uint8')
        savePath = self.IMG_PATH + self.IMG_NAME+'_em.png'  # Recovery IMG
        io.imsave(savePath, saveIMG)
        io.imshow(saveIMG)
        plt.show()
        return savePath
##接口函数，提取信息
    def Extracted(self,FILE_NAME,Ke):
        #EmIMG = io.imread(EmIMG_PATH)
        self.IMG_NAME = FILE_NAME.split('.', -1)[0]
        EmIMG = self.preprocess(self.IMG_PATH + FILE_NAME)
        RIMG = EmIMG[:, :, 0]
        GIMG = EmIMG[:, :, 1]
        BIMG = EmIMG[:, :, 2]
        dataR = self.single_channel_Extracted(RIMG,Ke)
        dataG = self.single_channel_Extracted(GIMG,Ke)
        dataB = self.single_channel_Extracted(BIMG,Ke)

        data = str(dataR)+str(dataG)+str(dataB)
        return data

    def single_channel_Embedded(self,EIMG,sData):
        sData = tool.get_uint8(sData)
        E_IMG = RDHEI.blocking(self,EIMG)
        E_IMG = E_IMG.astype('uint8')
        PR = E_IMG[0,:]
        PR = PR.reshape(1,-1)
        PS = E_IMG[1,0]
        p_err = 1
        PN_FLAG = np.zeros((self.s*self.s,self.n))
        PN_FLAG[0,:] = -1 #PR
        PN_FLAG[1,0] = -1 #PS

        for i in range(self.n):
            for j in range(1,4):
                e = 0
                a = PR[0,i]
                b = E_IMG[j,i]
                # if(a>=b):e= a-b
                # else: e=b-a
                e = -1*b+a
                if(abs(e)>p_err):
                    PN_FLAG[j,i] = 0
                elif e == -1:
                    PN_FLAG[j,i] = 1
                elif e == 0:
                    PN_FLAG[j,i] = 2
                elif e == 1:
                    PN_FLAG[j,i] = 3
        #STEP 3 PBTL
        PE_INDEX = np.argwhere(PN_FLAG != -1)
        #PN = np.zeros((1,1))
        PN = ""
        for i in range(len(PE_INDEX)-1):
            tmp_idx = PE_INDEX[i]
            tmp = PN_FLAG[tmp_idx[0],tmp_idx[1]]
            A = E_IMG[tmp_idx[0],tmp_idx[1]]
            if tmp == 0:
                A_bit = tool.uint2bit_num(A)
                PN += A_bit[len(A_bit)-2:len(A_bit)] #last two bits of A
                #PN += A_bit[0:2]
                A = tool.bits_modi(A,'00')
            elif tmp==1:
                A = tool.bits_modi(A,'10')
            elif tmp==2:
                A = tool.bits_modi(A,'01')
            elif tmp==3:
                A = tool.bits_modi(A,'11')
            E_IMG[tmp_idx[0],tmp_idx[1]] = A
        # STEP 4 PAYLOAD EMBED
        #ifb = PN.rfind('b')
        n_PN =np.argwhere(PN_FLAG==0).size
        n_PE = np.argwhere(PN_FLAG>0).size
        n_PAYLOAD = (8-2)*n_PE-2*n_PN-8

        PE_INDEX = np.argwhere(PN_FLAG>0)
        bit_data = tool.uint2bit(sData)
        PAYLOAD = tool.uint2bit_num(PS)+tool.uint2bit(sData) #+PN+
        n_PAYLOAD = len(PAYLOAD)
        nstr_PAYLOAD = str(n_PAYLOAD)
        n_nstr = len(nstr_PAYLOAD)
        nbit_PAYLOAD = tool.uint2bit(tool.get_uint8(nstr_PAYLOAD))
        PAYLOAD_HEAD = tool.uint2bit_num(n_nstr)+nbit_PAYLOAD
        PAYLOAD = PAYLOAD_HEAD+PAYLOAD

        k = 0
        for i in range(len(PE_INDEX)):
            tmp_idx = PE_INDEX[i]
            tmp = PN_FLAG[tmp_idx[0], tmp_idx[1]]
            A = E_IMG[tmp_idx[0], tmp_idx[1]]
            for j in range(0,6):
                if(k>len(PAYLOAD)-1):break
                A_bit = tool.bit_modi(A,j,PAYLOAD[k])
                A = int(A_bit,2)
                k = k+1
            E_IMG[tmp_idx[0], tmp_idx[1]] = A
        EMIMG = self.unblocking_two(E_IMG)
        return EMIMG
    def single_channel_Extracted(self,EmIMG,Ke):
        Em_IMG = self.blocking(EmIMG)
        Em_IMG = Em_IMG.astype("uint8")
        #GROUPING
        PR = Em_IMG[0,:]
        PS = Em_IMG[1,0]
        PN_FLAG = np.zeros((self.s * self.s, self.n))
        PN_FLAG[0, :] = -1  # PR
        PN_FLAG[1, 0] = -1  # PS
        BIAS = np.zeros((self.s * self.s, self.n))
        for i in range(self.n):
            for j in range(1,4):
                A = Em_IMG[j,i]
                R_bit = tool.uint2bit_num(A)
                #R_bit = R_bit[len(R_bit)-2:len(R_bit)] #FLAG BITS--LAST TWO BIT
                R_bit = R_bit[6:8]
                R_bit = int(R_bit,2)
                if(R_bit == 0):
                    PN_FLAG[j,i] = 0
                elif(R_bit == 2):
                    PN_FLAG[j,i] = 1
                    BIAS[j,i] = -1
                elif(R_bit == 1):
                    PN_FLAG[j,i] = 2
                    BIAS[j,i] = 0
                elif(R_bit == 3):
                    PN_FLAG[j,i] = 3
                    BIAS[j,i] = 1
        #extract from PE
        PE_INDEX = np.argwhere(PN_FLAG>0)
        ED_bit = "" #embedded data
        for i in range(len(PE_INDEX)):
            tmp_idx = PE_INDEX[i]
            tmp = PN_FLAG[tmp_idx[0], tmp_idx[1]]
            A = Em_IMG[tmp_idx[0], tmp_idx[1]]
            #for j in range(0,6):
            A_bit = tool.uint2bit_num(A)
            ED_bit += A_bit[0:6]

        #get length of Embedding data
        n_nstr = int(ED_bit[0:8],2)
        char_PAYLOAD = ""
        for i in range(1,n_nstr+1):
            char_PAYLOAD += str(int(ED_bit[8*i:8*(i+1)],2)-48) #ASCII change to num to str
        n_PAYLOAD = int(char_PAYLOAD)
        #CUT THE HEAD and CUT THE REST(unembedded)
        ED_bit = ED_bit[(n_nstr+1)*8:(n_nstr+1)*8+n_PAYLOAD]
        edlen = len(ED_bit)
        #recover PS PN
        PN_INDEX = np.argwhere(PN_FLAG==0)
        # n_pn = len(PN_INDEX)
        # k = 0
        # for i in range(n_pn):
        #     tmp_idx = PN_INDEX[i]
        #     tmp = PN_FLAG[tmp_idx[0], tmp_idx[1]]
        #     A = Em_IMG[tmp_idx[0], tmp_idx[1]]
        #     A = int(tool.bit_modi(A,0,ED_bit[k]),2)
        #     A = int(tool.bit_modi(A,1, ED_bit[k+1]),2)
        #     k = k+2
        #     Em_IMG[tmp_idx[0], tmp_idx[1]] = A
        #recover ED
        ED_bit = ED_bit[8:len(ED_bit)-1]
        ED = ""
        for i in range(int(len(ED_bit)/8)):
            ED += chr(int(ED_bit[i*8:(i+1)*8],2))
        for i in range(len(PE_INDEX)):
            tmp_idx = PE_INDEX[i]
            tmp = PN_FLAG[tmp_idx[0], tmp_idx[1]]
            R_PX = PR[tmp_idx[1]]
            Em_IMG[tmp_idx[0], tmp_idx[1]] = R_PX+BIAS[tmp_idx[0], tmp_idx[1]]
        #EmIMG = self.unblocking(Em_IMG)
        return ED
        pass
    def single_channel_Encrypted(self,sIMG,K):
        # self.n = int((self.height*self.width)/(self.s*self.s))
        # self.n_row = int(self.height/self.s)
        # self.n_col = int(self.width/self.s)
        IMGBLK = RDHEI.blocking(self,sIMG)
        #HIMG = imagehash.dhash(IMGBLK)
        #HK = hash()
        #todo 裂开了，没找到对矩阵做哈希的api,能否调用在线的？
        Ke = tool.datahash(IMGBLK,K)
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

    def preprocess(self,IMG_PATH):
        IMG = io.imread(IMG_PATH)
        self.height = len(IMG)
        self.width = len(IMG[0])
        self.n = int((self.height * self.width) / (self.s * self.s))
        self.n_row = int(self.height / self.s)
        self.n_col = int(self.width / self.s)
        return IMG

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

    def unblocking_two(self,BLK):
        k = 0
        BLK = BLK.T.reshape(-1,2,2)
        EIMG = np.zeros((self.height,self.width))

        for i in range(self.n_row):
            for j in range(self.n_col):
                #BLK[k,:,:] = BLK[k,:,:].T
                EIMG[i*self.s:i*self.s+self.s,
                    j*self.s:j*self.s+self.s] = BLK[k,:,:]
                k = k+1
        return EIMG