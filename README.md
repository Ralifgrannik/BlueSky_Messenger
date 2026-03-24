# BlueSky_Messenger
    ICQ-style E2EE messenger.
    ICQ мессенджер с E2EE шифрованием.

<table border="0">
  <tr>
    <td><img width="500" alt="auth_1" src="https://github.com/user-attachments/assets/eacc15f7-ee33-4339-9608-7ad636be8888" /></td>
    <td><img width="500" alt="auth_2" src="https://github.com/user-attachments/assets/eba524db-69fb-4ac6-833b-b1ac18af94a8" /></td>
  </tr>
  <tr>
    <td><img width="500" alt="main_1" src="https://github.com/user-attachments/assets/865f8ed0-6eca-4666-b991-78a6edf1212d" /></td>
    <td><img width="500" alt="main_2" src="https://github.com/user-attachments/assets/d3c6827d-a61f-4068-93b6-4d02517d0268" />
</td>
  </tr>
</table>


## 🛠 Инструкция по развертыванию сервера BlueSky
Эта инструкция предназначена для чистой ОС **Ubuntu 22.04 / 24.04**.

### 1. Подготовка системы
Первым делом нужно установить Python и инструменты для работы с виртуальным окружением.
1. Подключитесь к серверу по SSH (например, с помощью **PuTTY**). 
2. Используйте данные от вашего хостинга (IP, логин `root`, пароль).
3. В терминале пропишите:
```bash
    sudo apt update && sudo apt upgrade -y
    sudo apt install python3 python3-pip python3-venv screen -y
```

### 2. Создание папки и окружения
Чтобы библиотеки проекта не конфликтовали с системными, создаем изолированную среду:
```bash
    mkdir bluesky_server && cd bluesky_server
    python3 -m venv venv
    source venv/bin/activate
```
*После этого в начале строки терминала должно появиться (venv).*

### 3. Установка библиотек
Теперь устанавливаем все библиотеки, что нужны для работы нашего мессенджера:
```bash
    pip install flask flask-socketio eventlet werkzeug cryptography
```

### 4. Создание файла сервера
Создаем файл `server.py` и вставляем туда код сервера. Проще всего это сделать через `nano`:
1. Пропишите:
    ```bash
    nano server.py
    ```
2. Вставьте код сервера (правая кнопка мыши в PuTTY).
3. Сохраните изменения: **Ctrl+O** -> **Enter** -> **Ctrl+X**.

### 5. Настройка портов (Firewall)
Нужно открыть порт 5000, чтобы клиенты могли достучаться до сервера:
```bash
    sudo ufw allow 5000
    sudo ufw enable
```

### 6. Запуск в фоновом режиме (Screen)
Чтобы сервер не выключился после закрытия терминала:

1. **Создаем сессию:**
    ```bash
    screen -S bluesky
    ```
2. **Запускаем сервер** (убедитесь, что вы в `(venv)`):
    ```bash
    python3 server.py
    ```
3. **Важно:** Чтобы выйти из сессии и оставить сервер работать, нажми **Ctrl+A**, затем сразу кнопку **D**.

### 7. Использование
Запускаете BlueSky Messenger.exe и общаетесь, когда вы оба онлайн.

