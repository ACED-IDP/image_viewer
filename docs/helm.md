# HELM charts

## image-viewer

* [This chart](https://github.com/ACED-IDP/gen3-helm/blob/4eec2911dc21aba8e5c49cbc174c31fa77e501a3/helm/image-viewer/templates/deployment.yaml#L58-L62) deploys a simple image viewer that can be used to view images stored in a Gen3 data commons.
* [This nginx conf](https://github.com/ACED-IDP/gen3-helm/blob/79ea16e5785d6523e04e40ef940e9d5d37a8790e/helm/revproxy/gen3.nginx.conf/image-viewer-service.conf#L1-L9) publishes the image viewer at /image-viewer 

### Key values
* values.service.port: The port the service listens on (default: 8000)
* env.BASE_URL: The base URL of the Gen3 data commons (default: /aviator/?image_url=)

## aviator
* [This chart](https://github.com/ACED-IDP/gen3-helm/blob/79ea16e5785d6523e04e40ef940e9d5d37a8790e/helm/viv/templates/deployment.yaml#L62) deploys our fork of the Aviator image viewer that supports reading the image and offsets from signed urls.
* [This nginx conf](https://github.com/ACED-IDP/gen3-helm/blob/9ec32e2204241fbfcbc2b86f556b55cc4a0ae880/helm/revproxy/gen3.nginx.conf/viv-service.conf#L1-L9) publishes the image viewer at /image-viewer 

### Key values
* values.service.port: The port the service listens on (default: 8000)
