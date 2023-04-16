import datetime
import keyboard
import logging
from pick import pick
import sqlite3
import configparser
import db_helper

logging.basicConfig(filename='kettle.log',
                    filemode='a',
                    level=logging.INFO,
                    encoding='UTF-8',
                    format='%(asctime)s %(message)s')


class Kettle:
    def __init__(self, brand, model, boiled_time, volume, power, db_path):
        self.brand = brand
        self.model = model
        self.volume = float(volume)
        self.boiled_time = boiled_time
        self.power = int(power)
        self.water = 0
        self.is_heating = False
        self.history_db = sqlite3.connect(db_path)
        logging.info(f'{self}\n')
        self.show_selector()

    def __str__(self):
        return f'Производитель {self.brand}\nМодель {self.model}\nОбъем {self.volume}\nМощность {self.power}\nВоды в ' \
               f'чайнике {self.water}'

    def pour_into(self, water: str) -> None:
        """
        pour_water функция, чтобы налить воды
        :param water: str
        :return: None
        """
        logging.info(f'Попытка налить: {water}')
        try:
            water = float(water)
        except ValueError:
            logging.warning('Ошибка в pour_water в water неправильный аргумент')
            print('Ошибка ввода')
            return
        if not (0 < water < 1.0):
            logging.info('Попытка налить количество воды вне промежутка от 0 до 1')
            return
        if self.volume < water:
            logging.info(f'{water} Объем чайника меньше')
            print('Объем чайника меньше')
        if self.water + water > self.volume:
            answer = f'Превышен объем чайника {self.volume} Получающийся объем при заливании {self.water + water}'
            logging.info(answer)
            print(answer)
        else:
            self.water = self.water + water
            pour_into_id = db_helper.get_operation_by_name(self.history_db, db_helper.POUR_INTO)[0][0]
            db_helper.add_history_record(self.history_db, datetime.datetime.now(), pour_into_id)

    def is_need_to_continue(self) -> None:
        """
        is_need_to_continue функция, которая возвращает в главное меню
        :return: None
        """
        if input('Продолжить взаимодействие с чайником? Y/N: ').lower() == 'y' or 'н':
            self.show_selector()
        else:
            exit()

    def pour_out(self) -> None:
        """
        pour_out_water функция, чтобы вылить воду
        :return: None
        """
        self.water = 0
        pour_out_id = db_helper.get_operation_by_name(self.history_db, db_helper.POUR_OUT)[0][0]
        db_helper.add_history_record(self.history_db, datetime.datetime.now(), pour_out_id)
        logging.info(f'Вылили воду. В чайнике {self.water}')

    def turn_on(self, heating_time: int) -> None:
        """
        turn_on функция нагрева чайника, с возможностью остановки нагрева
        :param heating_time: int
        :return:
        """
        temp_water = 24
        finish_temp = 100
        delta_temp = (finish_temp - temp_water) / heating_time
        start_time = datetime.datetime.now()
        on_id = db_helper.get_operation_by_name(self.history_db, db_helper.ON)[0][0]
        db_helper.add_history_record(self.history_db, start_time, on_id)
        self.is_heating = True
        if self.water == 0:
            print('Чайник пуст! Залей воду перед включением!')
            logging.info('Попытка включить нагрев без воды!')
        else:
            key_timestamp = [start_time + datetime.timedelta(seconds=i) for i in range(1, heating_time + 1)]
            while temp_water < finish_temp and self.is_heating:
                curr_time = datetime.datetime.now()
                if len(key_timestamp) == 0:
                    break
                if curr_time > key_timestamp[0]:
                    del key_timestamp[0]
                    temp_water += delta_temp
                    print(round(temp_water, 2))
                    logging.info(f'Чайник нагрелся до {temp_water}')
                if keyboard.is_pressed('ALT'):
                    self.is_heating = False
            if not self.is_heating:
                print('Не нагрелся')
                logging.info('Чайник не нагрелся')
            else:
                logging.info(f'Чайник нагрелся до {temp_water}')
                print('Нагрелся')

    def show_selector(self):
        title = 'Что хочешь сделать?'
        options = ['Налить воды', 'Вылить воду', 'Включить чайник', 'Параметры', 'Выход']
        options, index = pick(options, title, indicator='=>', default_index=0)
        if index == 0:
            volume_water = input('Сколько литров налить воды? От 0 до 1.0: ')
            self.pour_into(volume_water)
        if index == 1:
            self.pour_out()
        if index == 2:
            self.turn_on(self.boiled_time)
        if index == 3:
            print(self)
            logging.info(f'Пользователь запросил параметры чайника')
        if index == 4:
            logging.info('Выход из программы')
            exit()
            off_id = db_helper.get_operation_by_name(self.history_db, db_helper.OFF)[0][0]
            db_helper.add_history_record(self.history_db, datetime.datetime.now(), off_id)
        self.is_need_to_continue()


cfg = configparser.ConfigParser()
cfg.read('kettle.cfg')
kettle_1 = Kettle(cfg['KETTLE']['Brand'],
                  cfg['KETTLE']['Model'],
                  int(cfg['KETTLE']['TimeToBoiledUp']),
                  float(cfg['KETTLE']['Volume']),
                  int(cfg['KETTLE']['Power']),
                  cfg['DB']['DBPath'])
