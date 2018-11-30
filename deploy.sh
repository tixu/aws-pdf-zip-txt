#!/bin/bash
echo 'deleting zip file';
rm handler.zip ; 
echo 'zipping archive'
zip -r handler-fanin.zip *;
echo 'uploading function'
aws --profile user s3 cp handler-fanin.zip s3://smals-ocr-deploy;
#echo 'deploying function'
#aws lambda update-function-code --s3-bucket lambdazip2 --s3-key handler-zip.zip --function-name Zip  --region eu-central-1 --profile user

