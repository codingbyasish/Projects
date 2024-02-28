
##Compressing the data
import zlib, base64

data = open('demo.txt','r').read()
data_bytes = bytes(data,'utf-8')
compressed_data= base64.b64encode(zlib.compress(data_bytes,9))
decoded_data = compressed_data.decode('utf-8')
compressed_file =  open('compressed.txt','w')
compressed_file.write(decoded_data)


##Decompressing the data
decompressed_data = zlib.decompress(base64.b64decode(compressed_data))
print(decompressed_data)





## Compress Function

import zlib, base64

def compress(inputfile,outputfile):
    data = open('demo.txt','r').read()
    data_bytes = bytes(data,'utf-8')
    compressed_data= base64.b64encode(zlib.compress(data_bytes,9))
    decoded_data = compressed_data.decode('utf-8')
    compressed_file =  open(outputfile,'w')
    compressed_file.write(decoded_data)


compress('demo.txt','ot.txt')

## Decompress Function
def decompress(inputfile,outputfile):
    file_content=open(inputfile,'r').read()
    encoded_data = file_content.encode('utf-8')
    decompressed_data = zlib.decompress(base64.b64decode(compressed_data))
    decoded_data= decompressed_data.decode('utf-8')
    file= open(outputfile,'w')
    file.write(decoded_data)
    file.close()

decompress('ot.txt','dc1.txt')
    

def compression(i,o):
    
