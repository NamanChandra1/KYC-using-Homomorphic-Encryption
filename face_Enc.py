import tenseal as ts
from deepface import DeepFace
import base64
import math



def face_enc(img1_path,img2_path):
    img1_embedding = DeepFace.represent(img1_path,model_name = 'Facenet')
    img2_embedding = DeepFace.represent(img2_path,model_name = 'Facenet')
    def write_data(file_name,file_content):
        if type(file_content)==bytes:
            file_content = base64.b64encode(file_content)
        with open(file_name,'wb') as f:
            f.write(file_content)
        
    def read_data(file_name):
        with open(file_name,'rb') as f:
            file_content = f.read()
        return base64.b64decode(file_content)
    context = ts.context(ts.SCHEME_TYPE.CKKS,poly_modulus_degree=8192, coeff_mod_bit_sizes = [60,40,40,60])
    context.generate_galois_keys()
    context.global_scale = 2**40
    secret_context = context.serialize(save_secret_key = True)
    type(secret_context)
    write_data(file_name = "secret.txt",file_content = secret_context)
    context.make_context_public()
    public_context = context.serialize()
    write_data(file_name = "public.txt",file_content = public_context)
    del context, secret_context, public_context
    
    context = ts.context_from(read_data("secret.txt"))
    enc_v1 = ts.ckks_vector(context, img1_embedding)
    enc_v2 = ts.ckks_vector(context, img2_embedding)
    
    write_data(file_name = "enc_v1.txt", file_content = enc_v1.serialize())
    write_data(file_name = "enc_v2.txt", file_content = enc_v2.serialize())
    del context, enc_v1,enc_v2
    
    context = ts.context_from(read_data("public.txt"))
    enc_v1 = ts.lazy_ckks_vector_from(read_data("enc_v1.txt"))
    enc_v2= ts.lazy_ckks_vector_from(read_data("enc_v2.txt"))
    
    enc_v1.link_context(context)
    enc_v2.link_context(context)
    
    euclidean_squared = enc_v1-enc_v2
    euclidean_squared = euclidean_squared.dot(euclidean_squared)
    write_data(file_name = "euclidean_squared.txt",file_content = euclidean_squared.serialize())
    del context,enc_v1,enc_v2,euclidean_squared
    
    context = ts.context_from(read_data("secret.txt"))
    
    euclidean_squared = ts.lazy_ckks_vector_from(read_data("euclidean_squared.txt"))
    euclidean_squared.link_context(context)
    
    euclidean_distance = math.sqrt(euclidean_squared.decrypt()[0])
    print(euclidean_distance)
    
    if euclidean_distance<13.5:
        return 1
    else:
        return 0

# face_enc(img1_path,img2_path)






