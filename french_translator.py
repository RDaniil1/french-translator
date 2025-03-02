from PyQt5.uic import loadUi
from PyQt5.QtWidgets import QDialog, QApplication, QMessageBox

from text_to_num import text2num
from num2words import num2words

import roman
import sys
from pathlib import Path
from itertools import chain


class MainWindow(QDialog):
    def __init__(self):
        super(QDialog, self).__init__()
        UI_PATH = Path(__file__).parent.joinpath('form.ui')
        loadUi(UI_PATH, self)
        self.pushButton.clicked.connect(self.translate_to_arabic_roman)

        self.hundreds = [num for num in range(100, 1000)]
        self.certain_dozens = [num for num in chain([10], range(20, 70), range(80, 90))]
        self.seventies_nineties = [num for num in chain(range(70, 80), range(90, 100))]
        self.eleven_to_nine_teen = [num for num in range(11, 20)]
        self.dozens_seventies_nineties = [num for num in chain(range(1, 10), range(70, 80), range(90, 100))]

        self.dozens  = [num for num in range(20, 100)]
        self.ten_nineteen = [num for num in range(10, 20)]
        self.units = [num for num in range(1, 10)]
        self.units_two = [num for num in range(2, 10)]


        # Custom lists to add errors for 70 and 90 numbers 
        self.seventy = [num for num in range(70, 80)]
        self.ninety = [num for num in range(90, 100)]

        self.analyzed_numbers = []
        # Check for incorrect input 
        self.nums_from_french: list[int] = []

    def get_num_type(self, number: int, *args) -> str:
        position = ''
        if len(args) != 0: 
            position = args[0] 

        number_dispatcher = {
            number in self.hundreds : 'сотен',
            number in self.certain_dozens: 'десяток',
            number in self.seventies_nineties and position == 'First': 'единиц',
            number in self.seventies_nineties and position == 'Second': 'десяток',
            number in self.eleven_to_nine_teen: 'чисел от одинадцати до девятнадцати',
            number in self.dozens_seventies_nineties: 'единиц'
        }
        return number_dispatcher[True]

    def check_number_status(self, first_num: int, second_num: int) -> str:
        error_dispatcher = {
            (first_num in self.hundreds) and (second_num in self.hundreds) : 'После сотен не может быть сотен',
            (first_num == 10) and (second_num in range(1, 7)) : 'После десяти не может быть чисел от одного до семи',
            (first_num in self.dozens) and (first_num not in (self.seventy + self.ninety)) and (second_num not in self.units) : 
                f'После десяток не может быть {self.get_num_type(second_num)}',
            first_num in (self.ten_nineteen + self.units + self.seventy + self.ninety) : 
                f"После {self.get_num_type(first_num, 'First')} не может быть {self.get_num_type(second_num, 'Second')}"
        }

        responce = error_dispatcher[True]
        return 'OK' if not responce else responce

    def combine_num_pairs(self, additional_condition: str, is_hundreds_or_double: bool) -> None:
        for i in range(len(self.nums_from_french) - 1):
            if (i + 1) <= (len(self.nums_from_french) - 1) and eval(additional_condition): 
                if is_hundreds_or_double:
                    self.nums_from_french[i] *= self.nums_from_french[i + 1] 
                else:
                    self.nums_from_french[i] += self.nums_from_french[i + 1] 
                del self.nums_from_french[i + 1]
    
    def concat_if_exists(self, french_words: list[str]) -> None:
        # Concatenate 'et' and units with next word if exist
        for i in range(len(french_words) - 1):
            is_un_or_onze = (french_words[i + 1] == 'un' or french_words[i + 1] == 'onze')
            if french_words[i] == 'et' and is_un_or_onze:
                french_words[i] += ' ' + french_words[i + 1]
                del french_words[i + 1] 

    def number_analysis(self, word: str) -> str:
        if word == '': 
            return 'Строка не должна быть пустой'

        french_words = word.lower().split()

        # Replace 'zero' on 'zéro', if exist
        if 'zero' in french_words: 
            french_words = ' '.join(french_words).replace('zero', 'zéro').split()

        self.concat_if_exists(french_words)

        try:
            for french_word in french_words:
                self.nums_from_french += [text2num(french_word, lang='fr')]
        except ValueError:    
            return f"Несуществующее число '{french_word}'"

        # Erasing '-' symbol in input words
        french_words = ' '.join(french_words).replace('-', ' ').split() 
        self.concat_if_exists(french_words)

        # Convert values from french to numbers 
        self.nums_from_french.clear()
        for french_word in french_words:
            self.nums_from_french += [text2num(french_word, lang='fr', relaxed=True)]

        # Number analysis: 
        # Hundreds
        is_in_units_and_hundred = 'self.nums_from_french[i] in self.units_two and self.nums_from_french[i + 1] == 100'
        self.combine_num_pairs(is_in_units_and_hundred, True)

        # 2 * 40
        is_four_and_twenty = 'self.nums_from_french[i] == 4 and self.nums_from_french[i + 1] == 20'
        self.combine_num_pairs(is_four_and_twenty, True)

        # 17-19
        is_ten_and_seven_to_nine = 'self.nums_from_french[i] == 10 and self.nums_from_french[i + 1] in [7, 8, 9]'
        self.combine_num_pairs(is_ten_and_seven_to_nine, False)

        # Dozens
        is_sixty_or_eighty = 'self.nums_from_french[i] == 60 or self.nums_from_french[i] == 80'
        is_ten_nineteen_or_units = 'self.nums_from_french[i + 1] in self.ten_nineteen or self.nums_from_french[i + 1] in units'
        self.combine_num_pairs(is_sixty_or_eighty and is_ten_nineteen_or_units, False)

        for i in range(self.nums_from_french.__len__() - 1):
            status = self.check_number_status(self.nums_from_french[i], self.nums_from_french[i + 1])
            if status != 'OK': 
                return status
        
        self.analyzed_numbers = self.nums_from_french
        return 'OK'

    def lowercase_first_letter(self, string: str):
        if isinstance(string, str):
            return string[:1].lower() + string[1:] 
        else:
            return string 

    def lowercase_first_letters(self, words: str) -> str:
        result = ''
        for word in words.split():
            result += ' ' + self.lowercase_first_letter(word)
        return result[1:]

    def translate_to_arabic_roman(self) -> None:
        french_number = self.lowercase_first_letters(self.inputLineEdit.text())
        log_output = self.number_analysis(french_number) 

        if log_output == 'OK':
            french_number = ' '.join([str(num2words(num, lang='fr')) for num in self.analyzed_numbers])
            result_num = text2num(french_number, "fr", relaxed=True)
            self.resultArabic.setText(str(result_num)) 
            self.resultRoman.setText(roman.toRoman(result_num))
        else: 
            msg_box = QMessageBox()
            msg_box.setWindowTitle("Ошибка")
            msg_box.setText(log_output)
            msg_box.exec()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main = MainWindow()
    main.setWindowTitle("French words translation")
    main.show()
    sys.exit(app.exec())