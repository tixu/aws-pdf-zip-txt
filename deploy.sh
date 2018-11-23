#!/bin/bash
echo 'deleting zip file';
rm handler.zip ; 
echo 'zipping archive'
zip -r handler-zip.zip *;
echo 'uploading function'
aws --profile user s3 cp handler-zip.zip s3://lambdazip2;
echo 'deploying function'
aws lambda update-function-code --s3-bucket lambdazip2 --s3-key handler-zip.zip --function-name Zip  --region eu-central-1 --profile user

