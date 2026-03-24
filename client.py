import socketio
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
import customtkinter as ctk
from tkinter import messagebox


class BlueSkyClient(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("BlueSky Messenger")
        self.geometry("1000x650")
        ctk.set_appearance_mode("dark")

        self.sio = socketio.Client()
        self.username = None
        self.selected_chat = None
        self.temp_username = None
        self.last_msg_text = None

        self.setup_crypto()
        self.setup_socket_events()

        self.container = ctk.CTkFrame(self, fg_color="transparent")
        self.container.pack(fill="both", expand=True)

        self.show_welcome_screen()

    def setup_crypto(self):
        self.private_key = rsa.generate_private_key(
            public_exponent=65537, key_size=2048
        )
        self.pub_pem = self.private_key.public_key().public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ).decode('utf-8')

    def clear_container(self):
        for widget in self.container.winfo_children():
            widget.destroy()

    # ====================== ЭКРАНЫ ======================

    def show_welcome_screen(self):
        self.clear_container()
        frame = ctk.CTkFrame(self.container, fg_color="#1a1a1a", corner_radius=20)
        frame.place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(frame, text="BlueSky", font=("Verdana", 40, "bold"), text_color="#3498db").pack(pady=(40, 10))
        ctk.CTkLabel(frame, text="Добро пожаловать в безопасный мессенджер",
                     font=("Arial", 14), text_color="#777").pack(pady=(0, 30), padx=50)

        ctk.CTkButton(frame, text="Войти в аккаунт", fg_color="#3498db", hover_color="#2980b9",
                      width=250, height=45, font=("Arial", 15, "bold"),
                      command=self.show_login_screen).pack(pady=10)

        ctk.CTkButton(frame, text="Создать новый профиль", fg_color="transparent", border_width=1,
                      border_color="#3498db", width=250, height=45,
                      command=self.show_register_screen).pack(pady=(10, 40))

    def show_login_screen(self):
        self.clear_container()
        frame = ctk.CTkFrame(self.container, fg_color="#161b22", corner_radius=20,
                             border_width=1, border_color="#30363d")
        frame.place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(frame, text="Вход", font=("Arial", 24, "bold")).pack(pady=20)

        self.ent_login_user = ctk.CTkEntry(frame, placeholder_text="Ваш логин", width=300, height=45)
        self.ent_login_user.pack(pady=10, padx=40)

        self.ent_login_pass = ctk.CTkEntry(frame, placeholder_text="Пароль", show="*", width=300, height=45)
        self.ent_login_pass.pack(pady=10)

        ctk.CTkButton(frame, text="Войти ➤", fg_color="#238636", hover_color="#2ea043",
                      width=300, height=45, command=self.run_login).pack(pady=20)

        ctk.CTkButton(frame, text="← Назад", fg_color="transparent", width=100,
                      command=self.show_welcome_screen).pack(pady=10)

    def show_register_screen(self):
        self.clear_container()
        frame = ctk.CTkFrame(self.container, fg_color="#1e1e2e", corner_radius=20,
                             border_width=2, border_color="#3498db")
        frame.place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(frame, text="Регистрация", font=("Arial", 24, "bold"), text_color="#3498db").pack(pady=20)
        ctk.CTkLabel(frame, text="Выберите уникальное имя в сети",
                     font=("Arial", 12), text_color="#aaa").pack(pady=5)

        self.ent_reg_user = ctk.CTkEntry(frame, placeholder_text="Придумайте логин",
                                         width=300, height=45, fg_color="#2b2b3b")
        self.ent_reg_user.pack(pady=10, padx=40)

        self.ent_reg_pass = ctk.CTkEntry(frame, placeholder_text="Надежный пароль",
                                         show="*", width=300, height=45, fg_color="#2b2b3b")
        self.ent_reg_pass.pack(pady=10)

        ctk.CTkButton(frame, text="Зарегистрироваться", fg_color="#3498db", hover_color="#2980b9",
                      width=300, height=45, command=self.run_register).pack(pady=20)

        ctk.CTkButton(frame, text="Отмена", fg_color="transparent", text_color="#ff4444",
                      width=100, command=self.show_welcome_screen).pack(pady=10)

    # ====================== СОЕДИНЕНИЕ ======================

    def connect_server(self):
        if not self.sio.connected:
            try:
                self.sio.connect('http://144.31.227.175:5000')
                return True
            except Exception as e:
                messagebox.showerror("BlueSky", f"Не удалось подключиться к серверу\n{e}")
                return False
        return True

    def run_login(self):
        login_val = self.ent_login_user.get().strip()
        if not login_val:
            return
        if self.connect_server():
            self.temp_username = login_val
            self.sio.emit('login', {
                'username': login_val,
                'password': self.ent_login_pass.get().strip(),
                'pub_key': self.pub_pem
            })

    def run_register(self):
        reg_val = self.ent_reg_user.get().strip()
        if not reg_val:
            return
        if self.connect_server():
            self.temp_username = reg_val
            self.sio.emit('register', {
                'username': reg_val,
                'password': self.ent_reg_pass.get().strip()
            })

    # ====================== SOCKET EVENTS ======================

    def setup_socket_events(self):
        @self.sio.on('auth_response')
        def on_auth(data):
            self.after(0, lambda: self._handle_auth(data))

        @self.sio.on('update_users')
        @self.sio.on('search_results')
        def on_update(users):
            self.after(0, lambda: self.refresh_list(users))

        @self.sio.on('target_key')
        def on_key(data):
            pub_key = data.get('pub_key')
            self.after(0, lambda: self.send_encrypted_payload(pub_key))

        @self.sio.on('receive_msg')
        def on_msg(data):
            self.after(0, lambda: self.display_message(
                data.get('sender'), data.get('payload'), is_me=False
            ))

    def _handle_auth(self, data):
        if data.get('status') == 'success':
            self.username = self.temp_username
            self.setup_main_ui()
        elif data.get('status') == 'registered':
            messagebox.showinfo("BlueSky", "Аккаунт создан! Теперь войдите.")
            self.show_login_screen()
        else:
            messagebox.showerror("Ошибка", data.get('msg', 'Неизвестная ошибка'))

    # ====================== ГЛАВНЫЙ ИНТЕРФЕЙС ======================

    def setup_main_ui(self):
        self.clear_container()

        self.container.grid_columnconfigure(0, weight=0)
        self.container.grid_columnconfigure(1, weight=1)
        self.container.grid_rowconfigure(0, weight=1)

        # Sidebar
        self.sidebar = ctk.CTkFrame(self.container, width=280, fg_color="#121212", corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)

        self.search_entry = ctk.CTkEntry(self.sidebar, placeholder_text="🔍 Поиск людей...",
                                         height=35, fg_color="#1e1e1e")
        self.search_entry.pack(fill="x", padx=15, pady=20)
        self.search_entry.bind("<KeyRelease>", self.do_search)

        self.user_list_scroll = ctk.CTkScrollableFrame(self.sidebar, fg_color="transparent")
        self.user_list_scroll.pack(fill="both", expand=True, padx=5)

        # Chat area
        self.chat_main = ctk.CTkFrame(self.container, fg_color="#0b0e11", corner_radius=0)
        self.chat_main.grid(row=0, column=1, sticky="nsew")

        self.chat_header = ctk.CTkLabel(self.chat_main, text="BlueSky Cloud",
                                        font=("Arial", 18, "bold"), text_color="#555")
        self.chat_header.pack(pady=15)

        self.chat_display = ctk.CTkTextbox(self.chat_main, state="disabled",
                                           fg_color="#0b0e11", font=("Arial", 14))
        self.chat_display.pack(fill="both", expand=True, padx=30, pady=10)

        input_frame = ctk.CTkFrame(self.chat_main, fg_color="transparent")
        input_frame.pack(fill="x", side="bottom", padx=30, pady=25)

        self.msg_input = ctk.CTkEntry(input_frame, placeholder_text="Введите сообщение...", height=50)
        self.msg_input.pack(side="left", fill="x", expand=True, padx=(0, 15))
        self.msg_input.bind("<Return>", lambda e: self.send_flow())

        self.send_btn = ctk.CTkButton(input_frame, text="➤", width=60, height=50,
                                      fg_color="#3498db", command=self.send_flow)
        self.send_btn.pack(side="right")

    def do_search(self, event):
        q = self.search_entry.get().strip()
        if q and self.sio.connected:
            self.sio.emit('search_user', {'query': q})

    def refresh_list(self, users):
        for w in self.user_list_scroll.winfo_children():
            w.destroy()
        for u in users:
            if u == self.username:
                continue
            ctk.CTkButton(
                self.user_list_scroll,
                text=f"  @{u}",
                anchor="w",
                height=45,
                fg_color="transparent",
                hover_color="#2b5278",
                command=lambda name=u: self.select_chat(name)
            ).pack(fill="x", pady=2)

    def select_chat(self, user):
        self.selected_chat = user
        self.chat_header.configure(text=f"Чат с @{user}", text_color="#3498db")

    def send_flow(self):
        if not self.selected_chat or not self.username:
            return
        txt = self.msg_input.get().strip()
        if txt:
            self.last_msg_text = txt
            self.sio.emit('get_pub_key', {'target': self.selected_chat})

    def send_encrypted_payload(self, pub_key_pem):
        """Шифрование и отправка"""
        if not pub_key_pem:
            messagebox.showwarning("BlueSky", 
                f"@{self.selected_chat} сейчас не в сети.\nСообщение будет доставлено, когда он зайдёт.")
            # Показываем сообщение у себя сразу
            self.display_message("Вы", self.last_msg_text, is_me=True)
            self.msg_input.delete(0, 'end')
            return

        try:
            target_key = serialization.load_pem_public_key(pub_key_pem.encode('utf-8'))
            encrypted = target_key.encrypt(
                self.last_msg_text.encode('utf-8'),
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )

            self.sio.emit('private_msg', {
                'sender': self.username,
                'target': self.selected_chat,
                'payload': encrypted
            })

            # Показываем у себя сразу
            self.display_message("Вы", self.last_msg_text, is_me=True)
            self.msg_input.delete(0, 'end')

        except Exception as e:
            messagebox.showerror("Ошибка шифрования", str(e))
            print(f"Encryption error: {e}")

    def display_message(self, sender, data, is_me=False):
        """Отображение сообщения"""
        if not hasattr(self, 'chat_display'):
            return

        self.chat_display.configure(state="normal")

        if is_me:
            self.chat_display.insert("end", f"Вы: {data}\n")
        else:
            try:
                decrypted = self.private_key.decrypt(
                    data,
                    padding.OAEP(
                        mgf=padding.MGF1(algorithm=hashes.SHA256()),
                        algorithm=hashes.SHA256(),
                        label=None
                    )
                ).decode('utf-8')
                self.chat_display.insert("end", f"[{sender}]: {decrypted}\n")
            except Exception:
                self.chat_display.insert("end", f"[{sender}]: <Зашифрованное сообщение>\n")

        self.chat_display.see("end")
        self.chat_display.configure(state="disabled")


if __name__ == "__main__":
    app = BlueSkyClient()
    app.mainloop()