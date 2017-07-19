# Deploy
To run container
```
sudo docker build  -t web-300 .
sudo docker run -d -p 80:80 --name web-300 web-300 '/var/www/database.sh'
```
