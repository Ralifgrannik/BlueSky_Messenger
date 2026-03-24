# BlueSky_Massenger
ICQ messenger

🛠 Инструкция по развертыванию сервера BlueSky
Эта инструкция предназначена для чистой ОС Ubuntu 22.04 / 24.04.

1. Подготовка системы
Первым делом нужно установить Python и инструменты для работы с виртуальным окружением.
Подключитесь к серверу по SSH(например с помощью PuTTY. Там где вы купили/арендовали сервер вам обычно будет выдан ip, логин root, а под ним будет пароль).
Далее в терминале PuTTY пропишите:
    sudo apt update && sudo apt upgrade -y
    sudo apt install python3 python3-pip python3-venv screen -y

2. Создание папки и окружения
Чтобы библиотеки проекта не конфликтовали с системными, создаем изолированную среду:
    mkdir bluesky_server && cd bluesky_server
    python3 -m venv venv
    source venv/bin/activate
После этого в начале строки терминала должно появиться (venv).

3. Установка библиотек
Теперь устанавливаем всё, что нужно для работы нашего чата:
    pip install flask flask-socketio eventlet werkzeug

4. Создание файла сервера
Создаем файл server.py и вставь туда твой код. Проще всего это сделать через nano. Пропишите
    nano server.py
И далее вставьте туда код сервера(правая кнопка мыши). Вот так нужно сделать: Вставить код -> Ctrl+O -> Enter -> Ctrl+X

5. Настройка портов (Firewall)
Нужно открыть порт 5000, чтобы клиенты могли достучаться до сервера:
    sudo ufw allow 5000
    sudo ufw enable

6. Запуск в фоновом режиме (Screen)
Чтобы сервер не выключился после закрытия терминала, запускаем его внутри "экрана":
  6.1 Создаем сессию:
      screen -S bluesky
  6.2 Внутри сессии (если вылетело окружение, снова source venv/bin/activate) запускаем:
      python3 server.py
  6.3 Важно: Чтобы выйти из сессии и оставить сервер работать, нажми Ctrl+A, затем сразу кнопку D.

7. Запускаете BlueSky Messenger.exe и общаетесь, когда вы оба онлайн.
   
<img width="1248" height="849" alt="image" src="https://github.com/user-attachments/assets/71bc982a-a221-465a-8348-bdedef57c5a5" />
<img width="1251" height="848" alt="image" src="https://github.com/user-attachments/assets/eba524db-69fb-4ac6-833b-b1ac18af94a8" />
<img width="1250" height="847" alt="image" src="https://github.com/user-attachments/assets/865f8ed0-6eca-4666-b991-78a6edf1212d" />
<img width="1251" height="845" alt="image" src="https://github.com/user-attachments/assets/ed83a90d-4938-47b0-91c2-c3a03ab352ae" />


