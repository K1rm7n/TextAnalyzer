import sys
import requests
from bs4 import BeautifulSoup
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QTextEdit, QPushButton, QFileDialog, QInputDialog, QDialog, QLabel, QLineEdit, QMainWindow
from PyQt5.QtCore import Qt
from nltk import FreqDist
from docx import Document

class ResultWindow(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('Статистика')
        self.setGeometry(400, 400, 400, 300)

        self.label = QLabel(self)

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        self.setLayout(layout)

    def update_stats(self, stats):
        result_text = "\n".join([f"{key}: {value}" for key, value in stats.items()])
        self.label.setText(result_text)
        self.show()

class TextParserApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.stop_words = set()
        self.result_window = ResultWindow()
        self.init_ui()

    def init_ui(self):
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        self.text_edit = QTextEdit(self.central_widget)
        self.parse_button = QPushButton('Анализировать', self.central_widget)
        self.parse_button.clicked.connect(self.parse_content)
        self.open_file_button = QPushButton('Открыть файл', self.central_widget)
        self.open_file_button.clicked.connect(self.open_file)
        self.set_stop_words_button = QPushButton('Установить слова остановки', self.central_widget)
        self.set_stop_words_button.clicked.connect(self.set_stop_words)

        self.url_line_edit = QLineEdit(self.central_widget)
        self.add_text_from_url_button = QPushButton('Добавить текст с URL', self.central_widget)
        self.add_text_from_url_button.clicked.connect(self.add_text_from_url)

        layout = QVBoxLayout()
        layout.addWidget(self.url_line_edit)
        layout.addWidget(self.add_text_from_url_button)
        layout.addWidget(self.text_edit)
        layout.addWidget(self.parse_button)
        layout.addWidget(self.open_file_button)
        layout.addWidget(self.set_stop_words_button)

        self.central_widget.setLayout(layout)

        self.setGeometry(300, 300, 700, 600)
        self.setWindowTitle('Анализатор текста')

    def parse_content(self):
        content = self.text_edit.toPlainText()
        words = self.tokenize_text(content)
        words = [word for word in words if word.lower() not in self.stop_words]
        stats = self.calculate_statistics(words)

        self.result_window.update_stats(stats)
        self.result_window.show()

    def open_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, 'Открыть текстовый файл', '', 'Текстовые файлы (*.txt);;Документы Word (*.docx);;Все файлы (*)')
        if file_path:
            if file_path.endswith(".txt"):
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                    self.text_edit.setPlainText(content)
                    self.parse_content()
            elif file_path.endswith(".docx"):
                document = Document(file_path)
                content = "\n".join([paragraph.text for paragraph in document.paragraphs])
                self.text_edit.setPlainText(content)
                self.parse_content()

    def set_stop_words(self):
        user_input, ok_pressed = QInputDialog.getText(self, "Установить слова остановки", "Введите слова остановки (через запятую):")
        if ok_pressed and user_input:
            self.stop_words = set(user_input.lower().split(','))

    def tokenize_text(self, text):
        return text.split()

    def calculate_statistics(self, words):
        freq_dist = FreqDist(words)
        total_characters_with_spaces = sum(len(word) for word in words)
        total_characters_without_spaces = len(''.join(words))
        total_letters = sum(c.isalpha() for c in ''.join(words))
        foreign_words = sum(c.isalpha() and not c.isascii() for c in ''.join(words))
        total_punctuation = sum(c in ',.!?' for c in ''.join(words))

        stats = {
            'Общее количество слов': len(words),
            'Общее количество символов с пропусками': total_characters_with_spaces,
            'Общее количество символов без пропусков': total_characters_without_spaces,
            'Общее количество букв': total_letters,
            'Иностранные слова': foreign_words,
            'Общее количество знаков препинания': total_punctuation,
        }

        return stats

    def add_text_from_url(self):
        url = self.url_line_edit.text()
        if url:
            try:
                response = requests.get(url)
                soup = BeautifulSoup(response.text, 'html.parser')
                text_from_url = soup.get_text()
                cleaned_text = ' '.join(line.strip() for line in text_from_url.splitlines() if line.strip())
                self.text_edit.setPlainText(cleaned_text)
                self.parse_content()
            except Exception as e:
                print(f"Ошибка во время загрузки текста с URL: {e}")

    def closeEvent(self, event):
        event.ignore()
        self.hide()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    parser_app = TextParserApp()
    parser_app.show()
    sys.exit(app.exec_())
