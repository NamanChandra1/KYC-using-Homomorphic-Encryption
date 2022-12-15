from PIL import Image
from Crypto.Cipher import AES
import binascii, os
import numpy as np
import sys




def getImageMatrix(imageName):
    im = Image.open(imageName) 
    pix = im.load()
    image_size = im.size 
    data=''
    for width in range(int(image_size[0])):
        for height in range(int(image_size[1])):
                x=(pix[width,height])
                for t in x:
                    data+=chr(t)
    
    return data,image_size[0],image_size[1]

def getData(imageName):
    im = Image.open(imageName) 
    pix = im.load()
    image_size = im.size 
    data=''
    for width in range(int(image_size[0])):
        for height in range(int(image_size[1])):
                x=(pix[width,height])
                for t in x:
                    data+=chr(t)
    
    return data
    


def encrypt_AES_GCM(msg, secretKey):
    aesCipher = AES.new(secretKey, AES.MODE_GCM)
    ciphertext, authTag = aesCipher.encrypt_and_digest(msg)
    return (ciphertext, aesCipher.nonce, authTag)


def encyption(imageName,key,hash_):
    data,h,w=getImageMatrix(imageName)
    arr = bytes(data, 'utf-8')
    encryptedMsg = encrypt_AES_GCM(arr, key)
    encrypted_data=binascii.hexlify(encryptedMsg[0])
    mat_enc_data=[]

    for i in encrypted_data:
        mat_enc_data.append(i)
    
    ele_no = len(data)
    pp=len(mat_enc_data)//ele_no

    mat_enc_data=mat_enc_data[:h*w*3*pp]

    arr = np.array(mat_enc_data)

    arr_2d = np.reshape(arr, (h,w,3,pp))

    im = Image.new("RGB", (h,w ))
    pix = im.load()

    for i in range(h):
        for j in range(w):
            value=[0,0,0]
            for k in range(3):
                for x in range(pp):
                    value[k]+=arr_2d[i][j][k][x]
                value[k]%=256
            pix[i,j]=(value[0],value[1],value[2])

    im.save(hash_ + ".png", "PNG")
    return hash_ + ".png",data


