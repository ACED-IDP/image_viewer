# Cross-origin resource sharing (CORS)

The storage endpoint that the signed URLS are generated for must have the appropriate CORS configuration to allow the image viewer to access the images. The following is an example CORS configuration that allows the image viewer to access the images.

```json
[
    {
        "AllowedHeaders": [
            "*"
        ],
        "AllowedMethods": [
            "GET",
            "HEAD"
        ],
        "AllowedOrigins": [
            "*"
        ],
        "ExposeHeaders": [],
        "MaxAgeSeconds": 3000
    }
]
```

For AWS: In the AWS console, navigate to the S3 bucket that the images are stored in. Click on the "Permissions" tab and then click on the "CORS configuration" button. Paste the above configuration into the text box and click "Save".
For CEPH: The CORS configuration can be set in the CEPH configuration file. The configuration is similar to the above example.
    
A quick test script to check if the CORS configuration is correct is below:

```bash
$ curl -H "Origin: https://aced-training.compbio.ohsu.edu"   -H "Access-Control-Request-Method: GET"   -H "Access-Control-Request-Headers: X-Requested-With"   -X OPTIONS --verbose   https://aced-production-data-bucket.s3.amazonaws.com 2>&1  | grep -e "Access-Control-Allow-Methods: GET, HEAD" -e "200 OK" && echo "CORS enabled OK"  || echo "Please enable CORS"
Please enable CORS
$ curl -H "Origin: https://aced-training.compbio.ohsu.edu"   -H "Access-Control-Request-Method: GET"   -H "Access-Control-Request-Headers: X-Requested-With"   -X OPTIONS --verbose   https://aced-development-data-bucket.s3.amazonaws.com 2>&1  | grep -e "Access-Control-Allow-Methods: GET, HEAD" -e "200 OK" && echo "CORS enabled OK"  || echo "Please enable CORS"
< HTTP/1.1 200 OK
< Access-Control-Allow-Methods: GET, HEAD
CORS enabled OK
```