from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.config import Config
from kivy.core.window import Window
from kivy.metrics import dp
import mysql.connector

Config.set('graphics', 'width', '2340')
Config.set('graphics', 'height', '1080')

db_user = ' '
db_password = ' '
db_name = ' '
db = None



def connect_to_mysql(host):
    try:
        return mysql.connector.connect(host=host, user=db_user, password=db_password, database=db_name)
    except mysql.connector.Error as err:
        print(f"Eroare conexiune SQL: {err}")
        return None



class TableView(GridLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cols = 10
        self.spacing = dp(5)
        self.size_hint_y = None
        self.bind(minimum_height=self.setter('height'))
        self.max_rows = 10  

        column_labels = ['ID', 'Nume', 'Prenume', 'Gen', 'Media', 'Profil', 'An_Studiu', 'CNP', 'Nr_Telefon', 'Email']
        column_widths = [50, 150, 150, 50, 50, 150, 80, 150, 120, 400]  
        for label_text, width in zip(column_labels, column_widths):
            label = Label(text=label_text, size_hint_y=None, height=dp(60), width=dp(width), text_size=(dp(width), None),
                          halign='center', valign='middle', font_size='16sp', bold=True)
            label.bind(size=label.setter('text_size'))
            self.add_widget(label)



    def add_row(self, data):
        if len(self.children) / 10 < self.max_rows:
            column_widths = [50, 150, 150, 50, 50, 150, 80, 150, 120, 200] 
            for item, width in zip(data, column_widths):
                label = Label(text=str(item), size_hint_y=None, height=dp(60), width=dp(width), text_size=(dp(width), None),
                              halign='left', valign='middle', font_size='16sp')
                label.bind(size=label.setter('text_size'))
                self.add_widget(label)
        else:
            print("Nr maxim linii atins.")



class EvStud(App):
    
    db = None
    cursor = None

    def build(self):
        
        self.prompt_for_host()
        self.root_widget = BoxLayout(orientation='vertical', padding=10, spacing=5)
        return self.root_widget

    def prompt_for_host(self):
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        host_input = TextInput(text='localhost', hint_text='Introdu adresa IP', size_hint_y=None, height=dp(40), font_size='20sp')
        submit_button = Button(text='Connect', size_hint_y=None, height=dp(60), font_size='20sp')
        content.add_widget(host_input)
        content.add_widget(submit_button)

        self.popup = Popup(title="Introdu adresa IP", content=content, size_hint=(0.8, 0.4), auto_dismiss=False)
        submit_button.bind(on_press=lambda x: self.connect_and_initialize(host_input.text))
        self.popup.open()

    def connect_and_initialize(self, host):
        self.db = connect_to_mysql(host.strip())
        if self.db:
            self.cursor = self.db.cursor()
            self.popup.dismiss()
            self.initialize_ui()
        else:
            host_input = self.popup.content.children[1]
            host_input.text = ''
            host_input.hint_text = 'Conexiune esuata, incearca din nou'

    def initialize_ui(self):
        self.root_widget.add_widget(Label(text='EvStud', font_size='30sp', size_hint=(1, 0.1), bold=True))

        grid = GridLayout(cols=4, size_hint=(1, 0.2), spacing=5)
        self.input_id = TextInput(hint_text='ID Student', multiline=False, size_hint_y=None, height=dp(40), font_size='20sp')
        self.input_nume = TextInput(hint_text='Nume', multiline=False, size_hint_y=None, height=dp(40), font_size='20sp')
        self.input_prenume = TextInput(hint_text='Prenume', multiline=False, size_hint_y=None, height=dp(40), font_size='20sp')
        self.input_cnp = TextInput(hint_text='CNP', multiline=False, size_hint_y=None, height=dp(40), font_size='20sp')

        grid.add_widget(self.input_id)
        grid.add_widget(self.input_nume)
        grid.add_widget(self.input_prenume)
        grid.add_widget(self.input_cnp)

        self.root_widget.add_widget(grid)

        button_grid = GridLayout(cols=4, size_hint=(1, 0.1), spacing=5)
        button_grid.add_widget(Button(text='Search', on_press=self.search, size_hint_y=None, height=dp(40), font_size='20sp'))
        button_grid.add_widget(Button(text='Refresh', on_press=self.refresh, size_hint_y=None, height=dp(40), font_size='20sp'))
        button_grid.add_widget(Button(text='Reset', on_press=self.reset, size_hint_y=None, height=dp(40), font_size='20sp'))
        button_grid.add_widget(Button(text='Exit', on_press=self.exit, size_hint_y=None, height=dp(40), font_size='20sp'))

        self.root_widget.add_widget(button_grid)

        scroll_view = ScrollView(size_hint=(1, 0.6), bar_width=dp(25), scroll_type=['bars'], do_scroll_x=True, do_scroll_y=False)
        self.table_view = TableView(size_hint=(None, 1), width=4000)
        scroll_view.add_widget(self.table_view)

        self.root_widget.add_widget(scroll_view)

        self.refresh()

    def refresh(self, instance=None):
        self.cursor.execute("SELECT * FROM Student")
        self.table_view.clear_widgets()
        for student in self.cursor:
            self.table_view.add_row(student)

    def search(self, instance):
        search_text = self.input_nume.text
        self.cursor.execute("SELECT * FROM Student WHERE nume LIKE %s", (f"%{search_text}%",))
        self.table_view.clear_widgets()
        for student in self.cursor:
            self.table_view.add_row(student)

    def reset(self, instance):
        self.input_id.text = ''
        self.input_nume.text = ''
        self.input_prenume.text = ''
        self.input_cnp.text = ''

    def exit(self, instance):
        self.stop()

Window.clearcolor = (0.2, 0.2, 0.2, 1)

if __name__ == '__main__':
    EvStud().run()
