from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QWidget,
    QLabel,
    QSpinBox,
    QDoubleSpinBox,
    QFormLayout,
    QVBoxLayout,
    QLineEdit,
    QPushButton,
    QComboBox,
    QMessageBox,
)

import numpy as np

from system import System
from math import sqrt
import matplotlib.pyplot as plt

module = 'Промоделировать'
graph_1 = 'Построить зависимость от интенсивности генерации заявок'
graph_2 = 'Построить зависимость от интенсивности обработки заявок'
graph_3 = 'Построить зависимость от загрузки системы'
error_message = 'Ошибка ввода'

min_message_amount = 1
max_message_amount = 100000
min_probability = 0.00
max_probability = 1.00
step = 0.01


class MainPage(QWidget):
    def __init__(self):
        super().__init__()
        model_title = QLabel('Настройка модели')
        model_parameters = QFormLayout()
        self.model_time = QLineEdit()
        self.model_time.setText('1000')
        model_parameters.addRow(QLabel('Время моделирования: '), self.model_time)
        model = QVBoxLayout()
        model.addWidget(model_title)
        model.addLayout(model_parameters)

        generation_title = QLabel('Настройка появления заявок:')
        # generation_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.msg_number = QSpinBox()
        self.msg_number.setRange(min_message_amount, max_message_amount)
        self.msg_number.setValue(200)
        self.i1 = QDoubleSpinBox()
        self.i1.setSingleStep(0.01)
        msg_parameters1 = QFormLayout()
        msg_parameters1.addRow(QLabel('Общее число заявок: '), self.msg_number)
        self.d1 = QDoubleSpinBox()
        self.d1.setSingleStep(0.01)
        self.dropdown1 = QComboBox()
        self.dropdown1.addItem('интенсивность')
        self.dropdown1.addItem('параметры распределения')
        self.dropdown1.setStyleSheet('''* QComboBox {max-width: 250px;}''')
        self.dropdown1.currentIndexChanged.connect(self.__on_dropdown1_change)
        msg_parameters1.addRow(QLabel('Настроить, используя: '), self.dropdown1)

        msg_parameters1.addRow(QLabel('Интенсивность: '), self.i1)
        msg_parameters1.addRow(QLabel('Разброс: '), self.d1)
        generation_law = QLabel('Параметры равномерного распределения:')
        generation_law.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.a1 = QDoubleSpinBox()
        self.a1.setSingleStep(step)
        self.a1.setRange(-20, 20)
        self.a1.setDisabled(True)
        self.b1 = QDoubleSpinBox()
        self.b1.setSingleStep(step)
        self.b1.setRange(-20, 20)
        self.b1.setDisabled(True)
        generation_parameters = QFormLayout()
        generation_parameters.addRow(QLabel('a:'), self.a1)
        generation_parameters.addRow(QLabel('b:'), self.b1)
        generation = QVBoxLayout()
        generation.addWidget(generation_title)
        generation.addLayout(msg_parameters1)
        generation.addWidget(generation_law)
        generation.addLayout(generation_parameters)


        handling_title = QLabel('Настройка обработки заявок:')
        self.dropdown2 = QComboBox()
        self.dropdown2.addItem('интенсивность')
        self.dropdown2.addItem('параметры распределения')
        self.dropdown2.setStyleSheet('''* QComboBox {max-width: 250px;}''')
        self.dropdown2.currentIndexChanged.connect(self.__on_dropdown2_change)

        self.i2 = QDoubleSpinBox()
        self.i2.setSingleStep(0.01)
        self.d2 = QDoubleSpinBox()
        self.d2.setSingleStep(0.01)
        msg_parameters2 = QFormLayout()
        msg_parameters2.addRow(QLabel('Настроить, используя: '), self.dropdown2)
        msg_parameters2.addRow(QLabel('Интенсивность'), self.i2)
        msg_parameters2.addRow(QLabel('Разброс: '), self.d2)
        handling_law = QLabel('Параметры равномерного распределения:')
        handling_law.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.a2 = QDoubleSpinBox()
        self.a2.setSingleStep(step)
        self.a2.setRange(-20, 20)
        self.a2.setDisabled(True)
        self.b2 = QDoubleSpinBox()
        self.b2.setSingleStep(step)
        self.b2.setRange(-20, 20)
        self.b2.setDisabled(True)
        handling_parameters = QFormLayout()
        handling_parameters.addRow(QLabel('a:'), self.a2)
        handling_parameters.addRow(QLabel('b:'), self.b2)
        handling = QVBoxLayout()
        handling.addWidget(handling_title)
        handling.addLayout(msg_parameters2)
        handling.addWidget(handling_law)
        handling.addLayout(handling_parameters)

        self.avg_time_in_system = QLineEdit()
        self.expected_load = QLineEdit()
        self.actual_load = QLineEdit()
        results = QFormLayout()
        results.addRow(QLabel('Средее время ожидания: '), self.avg_time_in_system)
        results.addRow(QLabel('Расчётная загрузка системы'), self.expected_load)
        results.addRow(QLabel('Фактическая загрузка системы'), self.actual_load)
        queue = QVBoxLayout()
        queue.addLayout(results)

        system = QVBoxLayout()
        system.addLayout(model)
        system.addLayout(generation)
        system.addLayout(handling)
        button = QPushButton(module)
        button.clicked.connect(self.__model_system_load)
        graph_1_btn = QPushButton(graph_1)
        graph_1_btn.clicked.connect(self.__get_dependency_on_i1)
        graph_2_btn = QPushButton(graph_2)
        graph_2_btn.clicked.connect(self.__get_dependency_on_i2)
        graph_3_btn = QPushButton(graph_3)
        graph_3_btn.clicked.connect(self.__get_dependency_on_load)
        system.addWidget(button)
        system.addWidget(graph_1_btn)
        system.addWidget(graph_2_btn)
        system.addWidget(graph_3_btn)
        system.addLayout(queue)

        self.setLayout(system)

    def __model_system_load(self):
        try:
            model_time = int(self.model_time.text())
            if model_time <= 0: raise Exception()
        except:
            self.__error_msg('Время моделирования дожно быть целым положительным числом!')
            return

        try:
            msg_amount = int(self.msg_number.value())
            if msg_amount <= 0: raise Exception()
        except:
            self.__error_msg('Количество заявок должно быть целым положительным числом!')
            return

        generation_method = self.dropdown1.currentIndex()

        a1 = 0
        b1 = 0
        i1 = 0
        if generation_method == 0:
            try:
                i1 = float(self.i1.value())
                if i1 <= 0: raise Exception()
            except:
                self.__error_msg('Интенсивность генерации заявок - положительное число с плавающей запятой!')
                return
            try:
                d1 = float(self.d1.value())
                if d1 < 0: raise Exception()
            except:
                self.__error_msg('Разброс для генерации заявок - неотрицательное число, меньшее половины интенсивности!')
                return

            m1 = 1 / i1

            # I = 4 в условную единицу => M = 1 / I
            # D = 2, т.е. от 2 до 6 заявок в условную единицу, от (I - D) до (I + D)

            # M = (a + b) / 2 => a + b = 2M => a = 2M - b
            # D = (b - a)^2 / 12
            # 12D = (b - 2M + b)^2
            # 12D = 4 * (b - M)^2
            # b^2 - 2M * b + M^2 - 3D = 0 --- квадратное уравнение
            # Дискриминант = (2M)^2 - 4 * (M^2 - 3D) = 3D
            # Один из корней выйдет равен a, а другой b, но b должен быть больше, поэтому
            # b = M + sqrt(3D)
            # a = 2M - b = M - sqrt(3D)
            # Для примера выше: a = 4 - 2.44 = 1.56, b = 6.44
            # Проверка:
            # M = (a + b) / 2 = 4 = I (верно)
            # D = (b - a)^2 / 12 = 23,815 / 12 = 2 = D (верно)

            s = sqrt(3 * d1)
            a1 = m1 - s
            if a1 < 0:
                self.__error_msg('Разброс для генерации заявок слишком большой!')
                return
            b1 = m1 + s
        else:
            try:
                a1 = float(self.a1.value())
                b1 = float(self.b1.value())
                i1 = (a1 + b1) / 2
                if a1 < 0 or a1 >= b1: raise Exception()
            except:
                self.__error_msg('Параметры a и b - вещественные числа, причём a < b !')
                return

        a2 = 0
        b2 = 0
        i2 = 0
        if generation_method == 0:
            try:
                i2 = float(self.i2.value())
                if i2 <= 0: raise Exception()
            except:
                self.__error_msg('Интенсивность обслуживания заявок - положительное число с плавающей запятой!')
                return
            try:
                d2 = float(self.d1.value())
                if d2 < 0: raise Exception()
            except:
                self.__error_msg('Разброс для обслуживания заявок - неотрицательное число, меньшее половины интенсивности!')
                return

            m2 = 1 / i2

            s = sqrt(3 * d2)
            a2 = m2 - s
            if a2 < 0:
                self.__error_msg('Разброс для генерации заявок слишком большой!')
                return
            b2 = m2 + s
        else:
            try:
                a2 = float(self.a1.value())
                b2 = float(self.b1.value())
                i2 = (a2 + b2) / 2
                if a2 < 0 or a2 >= b2: raise Exception()
            except:
                self.__error_msg('Параметры a и b - вещественные числа, причём a < b !')
                return
        # print(f'a1 = {a1}, b1 = {b1}, a2 = {a2}, b2 = {b2}, step = {step}, msg = {msg_amount}')

        self.system = System(a1, b1, a2, b2, msg_amount, model_time)
        avg_time_in_system, i1_actual, i2_actual = self.system.event_driven()
        # eventful_max_length = self.system.event_driven()

        self.avg_time_in_system.setText("{:.2f}".format(avg_time_in_system))
        self.expected_load.setText("{:.2f}".format(i1 / i2))
        self.actual_load.setText("{:.2f}".format(i1_actual / i2_actual))

        # self.eventful_length.setText(str(eventful_max_length))

    def __get_dependency_on_i1(self):
        try:
            model_time = int(self.model_time.text())
            if model_time <= 0: raise Exception()
        except:
            self.__error_msg('Время моделирования дожно быть целым положительным числом!')
            return

        try:
            msg_amount = int(self.msg_number.value())
            if msg_amount <= 0: raise Exception()
        except:
            self.__error_msg('Количество заявок должно быть целым положительным числом!')
            return

        generation_method = self.dropdown1.currentIndex()

        a2 = 0
        b2 = 0
        i2 = 0
        if generation_method == 0:
            try:
                i2 = float(self.i2.value())
                if i2 <= 0: raise Exception()
            except:
                self.__error_msg('Интенсивность обслуживания заявок - положительное число с плавающей запятой!')
                return
            try:
                d2 = float(self.d1.value())
                if d2 < 0: raise Exception()
            except:
                self.__error_msg('Разброс для обслуживания заявок - неотрицательное число, меньшее половины интенсивности!')
                return

            m2 = 1 / i2

            s = sqrt(3 * d2)
            a2 = m2 - s
            if a2 < 0:
                self.__error_msg('Разброс для генерации заявок слишком большой!')
                return
            b2 = m2 + s
        else:
            try:
                a2 = float(self.a1.value())
                b2 = float(self.b1.value())
                i2 = (a2 + b2) / 2
                if a2 < 0 or a2 >= b2: raise Exception()
            except:
                self.__error_msg('Параметры a и b - вещественные числа, причём a < b !')
                return

        i1_range = np.arange(0.1, i2 - 0.1, 0.1)
        avg_times = []
        for i1 in i1_range:
            self.system = System(1 / i1, 1 / i1, a2, b2, msg_amount, model_time)
            avg_time_in_system, _, _ = self.system.event_driven()
            avg_times.append(avg_time_in_system)

        plt.plot(i1_range, avg_times)
        plt.ylabel('Среднее время ожидания обработки')
        plt.xlabel('Интенсивность генерации заявок')
        plt.title('Зависимость среднего времени ожидания \nот интенсивности генерации заявок')
        plt.show()

    def __get_dependency_on_i2(self):
        try:
            model_time = int(self.model_time.text())
            if model_time <= 0: raise Exception()
        except:
            self.__error_msg('Время моделирования дожно быть целым положительным числом!')
            return

        try:
            msg_amount = int(self.msg_number.value())
            if msg_amount <= 0: raise Exception()
        except:
            self.__error_msg('Количество заявок должно быть целым положительным числом!')
            return

        generation_method = self.dropdown1.currentIndex()

        a1 = 0
        b1 = 0
        i1 = 0
        if generation_method == 0:
            try:
                i1 = float(self.i1.value())
                if i1 <= 0: raise Exception()
            except:
                self.__error_msg('Интенсивность генерации заявок - положительное число с плавающей запятой!')
                return
            try:
                d1 = float(self.d1.value())
                if d1 < 0: raise Exception()
            except:
                self.__error_msg('Разброс для генерации заявок - неотрицательное число, меньшее половины интенсивности!')
                return

            m1 = 1 / i1

            # I = 4 в условную единицу => M = 1 / I
            # D = 2, т.е. от 2 до 6 заявок в условную единицу, от (I - D) до (I + D)

            # M = (a + b) / 2 => a + b = 2M => a = 2M - b
            # D = (b - a)^2 / 12
            # 12D = (b - 2M + b)^2
            # 12D = 4 * (b - M)^2
            # b^2 - 2M * b + M^2 - 3D = 0 --- квадратное уравнение
            # Дискриминант = (2M)^2 - 4 * (M^2 - 3D) = 3D
            # Один из корней выйдет равен a, а другой b, но b должен быть больше, поэтому
            # b = M + sqrt(3D)
            # a = 2M - b = M - sqrt(3D)
            # Для примера выше: a = 4 - 2.44 = 1.56, b = 6.44
            # Проверка:
            # M = (a + b) / 2 = 4 = I (верно)
            # D = (b - a)^2 / 12 = 23,815 / 12 = 2 = D (верно)

            s = sqrt(3 * d1)
            a1 = m1 - s
            if a1 < 0:
                self.__error_msg('Разброс для генерации заявок слишком большой!')
                return
            b1 = m1 + s
        else:
            try:
                a1 = float(self.a1.value())
                b1 = float(self.b1.value())
                i1 = (a1 + b1) / 2
                if a1 < 0 or a1 >= b1: raise Exception()
            except:
                self.__error_msg('Параметры a и b - вещественные числа, причём a < b !')
                return

        i2_range = np.arange(i1, 50, 0.1)
        avg_times = []
        for i2 in i2_range:
            self.system = System(a1, b1, 1 / i2, 1 / i2, msg_amount, model_time)
            avg_time_in_system, _, _ = self.system.event_driven()
            avg_times.append(avg_time_in_system)

        plt.plot(i2_range, avg_times)
        plt.ylabel('Среднее время ожидания обработки')
        plt.xlabel('Интенсивность обработки заявок')
        plt.title('Зависимость среднего времени ожидания \nот интенсивности обработки заявок')
        plt.show()

    def __get_dependency_on_load(self):
        try:
            model_time = int(self.model_time.text())
            if model_time <= 0: raise Exception()
        except:
            self.__error_msg('Время моделирования дожно быть целым положительным числом!')
            return

        try:
            msg_amount = int(self.msg_number.value())
            if msg_amount <= 0: raise Exception()
        except:
            self.__error_msg('Количество заявок должно быть целым положительным числом!')
            return

        load_range = np.arange(0.3, 0.99, 0.005)
        avg_times = []
        i2 = 10
        d1 = 0.1
        d2 = 0.1
        a2 = 1 / i2 -d2
        b2 = 1 / i2 +d2
        times = 5
        tmp = []
        for load in load_range:
            i1 = i2 * load
            a1 = 1 / i1 - d1
            b1 = 1 / i2 + d1
            for i in range(times):
                self.system = System(a1, b1, a2, b2, msg_amount, model_time)
                avg, _, _ = self.system.event_driven()
                tmp.append(avg)
            avg_time_in_system = sum(tmp) / len(tmp)

            print(i1, i2, 1/i1, 1/i2, avg_time_in_system)
            avg_times.append(avg_time_in_system)

        plt.plot(load_range, avg_times)
        plt.ylabel('Среднее время ожидания обработки')
        plt.xlabel('Загрузка системы')
        plt.title('Зависимость среднего времени ожидания \nот загрузки системы')
        plt.show()

    def __on_dropdown1_change(self, value):
        if value == 0:
            self.i1.setDisabled(False)
            self.d1.setDisabled(False)
            self.a1.setDisabled(True)
            self.b1.setDisabled(True)
        else:
            self.i1.setDisabled(True)
            self.d1.setDisabled(True)
            self.a1.setDisabled(False)
            self.b1.setDisabled(False)

    def __on_dropdown2_change(self, value):
        if value == 0:
            self.i2.setDisabled(False)
            self.d2.setDisabled(False)
            self.a2.setDisabled(True)
            self.b2.setDisabled(True)
        else:
            self.i2.setDisabled(True)
            self.d2.setDisabled(True)
            self.a2.setDisabled(False)
            self.b2.setDisabled(False)

    def __error_msg(self, text):
        msg = QMessageBox()
        msg.setText(text)
        msg.setWindowTitle(error_message)
        msg.exec()
