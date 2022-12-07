# Steps to update the verified publishers list. 

## 1) Run Selenium/firefox-standalone image

```docker run -d -e SE_EVENT_BUS_HOST=selenium-hub -e SE_EVENT_BUS_PUBLISH_PORT=4442 -e SE_EVENT_BUS_SUBSCRIBE_PORT=4443 -e SE_START_XVFB=false --shm-size="2g" selenium/standalone-firefox ```

## 2) List running containers
```docker ps```
## 3) Get Selenium/firefox-standalone ip address

```docker inspect -f '{{range.NetworkSettings.Networks}}{{.IPAddress}}{{end}}' <container_id>```

## 4) Run 

```python kg_utils/search_utils/url_detector.py  selenium-remote-ip-address```