from __future__ import print_function
import boto3
import io
import os
import zipfile
import glob
from PyPDF2 import PdfFileWriter, PdfFileReader,PdfFileMerger
from  tempfile import TemporaryDirectory, NamedTemporaryFile

s3 = boto3.resource('s3')
in_bucket  = os.getenv("input-bucket","smals-work-2")
out_bucket = os.getenv("output-bucket", "smals-ocr-bucket")


def F(event, context):
    for record in event['Records']: 
        print(record['eventID']) 
        print(record['eventName'])
        if (record['eventName']) != 'MODIFY':
            return 
        print(record['dynamodb']['NewImage']['instance']['N'])
        worker = int(record['dynamodb']['NewImage']['instance']['N'] )
        if worker == 0:
            prefix = record['dynamodb']['NewImage']['ID']['S']
            process_bucket(prefix )
        else:
            print ("no need to work for {}")
    print('Successfully processed %s records.' % str(len(event['Records'])))
#end_def

def process_bucket (prefix):
     with TemporaryDirectory(suffix="_zip",prefix='lambda_zip') as tmpdirname :
        print ("processing {} in {} : retrieving files from bucket ".format(prefix, tmpdirname))
        my_bucket = s3.Bucket(in_bucket)
        for object in my_bucket.objects.filter(Prefix = prefix):
                 
              response  = object.get()
              fileName = object.key.replace("/","_")
              fullPath = os.path.join(tmpdirname,fileName)
              print(fullPath)
              body = response['Body']
              try:
                  with io.FileIO(fullPath, 'w') as file:
                     while file.write(body.read(amt=512)):
                          pass
              except Exception as e:
                 print(e)
                 print('Error writing file')
                 raise e
#       zipArchive = zipFolder(prefix.replace("/","_"),tmpdirname)
        ocrPDF =  mergePDF(prefix.replace("/","_"),tmpdirname)
        s3.Object(out_bucket,"out/{}.pdf".format(prefix)).put(Body=open(ocrPDF,'rb'))

#end_def
def zipFolder(name,path):
    print("zipping folder")
    name = name + ".zip"
    fullName = os.path.join("/tmp/",name)
    T_zip = zipfile.ZipFile(fullName, 'w')

    for folder, subfolders, files in os.walk(path):
        for file in files:
             absfn = os.path.join(path,file)
             zfn = absfn[len(folder)+len(os.sep):]
             T_zip.write(absfn, zfn, compress_type = zipfile.ZIP_DEFLATED)
            
    T_zip.close()
    print("folder zipped {}".format(fullName))
    return fullName

def mergePDF (name, path): 
        fullName = os.path.join("/tmp/",name)
        pattern = "{}/*.pdf".format(path)
        print (pattern)
        paths = glob.glob(pattern)
        paths.sort()
        merger(fullName,paths)
        return fullName
#end_def


def merger(output_path, input_paths):
    pdf_merger = PdfFileMerger()
    file_handles = []

    for path in input_paths:
        pdf_merger.append(path)

    with open(output_path, 'wb') as fileobj:
        pdf_merger.write(fileobj)


 #end_def
