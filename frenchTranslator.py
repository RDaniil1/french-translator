from PyQt5.uic import loadUi
from PyQt5.QtWidgets import QDialog, QApplication, QMessageBox
from text_to_num import text2num
from num2words import num2words
import roman
import sys
from pathlib import Path


class MainWindow(QDialog):

    def __init__(self):
        super(QDialog, self).__init__()
        UI_PATH = Path(__file__).parent.joinpath('form.ui')
        loadUi(UI_PATH, self)
        self.pushButton.clicked.connect(self.TranslateFromFrenchToArabicAndRomanNumber)

    def __GetNumType(self, number: int, *args) -> str:

        position = ''
        if args.__len__() != 0: position = args[0] 

        if number in [num for num in range(100, 1000)]: return 'сотен'
        elif number in [num for num in range(20, 70)] + [num for num in range(80, 90)] + [10]: return 'десяток'
        elif number in [num for num in range(70, 80)] + [num for num in range(90, 100)] and position == 'First': return 'единиц'
        elif number in [num for num in range(70, 80)] + [num for num in range(90, 100)] and position == 'Second': return 'десяток'
        elif number in [num for num in range(11, 20)]: return 'чисел от одинадцати до девятнадцати'
        elif number in [num for num in range(1, 10)] + [num for num in range(70, 80)] + [num for num in range(90, 100)]: return 'единиц'

    def __CheckNumberStatus(self, firstNum: int, secondNum: int) -> str:
        
        hundreds = [num for num in range(100, 1000)]
        dozens  = [num for num in range(20, 100)]
        tenToNineteen = [num for num in range(10, 20)]
        units = [num for num in range(1, 10)]

        # Custom lists to add errors for 70 and 90 numbers 
        seventy = [num for num in range(70, 80)]
        ninty = [num for num in range(90, 100)]
            
        if (firstNum in hundreds) and (secondNum in hundreds): return 'После сотен не может быть сотен'
        elif (firstNum == 10) and (secondNum in range(1, 7)): return 'После десяти не может быть чисел от одного до семи'
        elif (firstNum in dozens) and (firstNum not in seventy and firstNum not in ninty) and (secondNum not in units): return f'После десяток не может быть {self.__GetNumType(secondNum)}'
        elif firstNum in tenToNineteen or firstNum in units or firstNum in seventy or firstNum in ninty: return f"После {self.__GetNumType(firstNum, 'First')} не может быть {self.__GetNumType(secondNum, 'Second')}"
          
        return 'OK'

    def __NumberAnalysis(self, word: str) -> str:

        if word == '': return 'Строка не должна быть пустой'

        frenchWords = word.lower().split()

        # Replace 'zero' on 'zéro', if exist
        if 'zero' in frenchWords: frenchWords = ' '.join(frenchWords).replace('zero', 'zéro').split()

        # Concatenate 'et' and units with next word if exist
        for i in range(len(frenchWords) - 1):
            if frenchWords[i] == 'et' and (frenchWords[i + 1] == 'un' or frenchWords[i + 1] == 'onze'):
                frenchWords[i] += ' ' + frenchWords[i + 1]
                del frenchWords[i + 1] 

        # Check for incorrect input 
        numsFromFrench: list[int] = []

        try:
            for frenchWord in frenchWords:
                numsFromFrench += [text2num(frenchWord, lang='fr')]
        except ValueError:    
            return f"Несуществующее число '{frenchWord}'"

        # Число не должно быть равным либо быть больше 1000, 0
        for i in range(len(numsFromFrench)):
            if numsFromFrench[i] == 1000: return 'Недопустимое число: 1000'
            elif numsFromFrench[i] == 0: return 'Недопустимое число: 0'

        # Erasing '-' symbol in input words
        frenchWords = ' '.join(frenchWords).replace('-', ' ').split() 

        # Concatenate 'et' and units with next word if exist
        for i in range(len(frenchWords) - 1):
            if frenchWords[i] == 'et' and (frenchWords[i + 1] == 'un' or frenchWords[i + 1] == 'onze'):
                frenchWords[i] += ' ' + frenchWords[i + 1]
                del frenchWords[i + 1] 

        # Convert values from french to numbers 
        numsFromFrench.clear()
        for frenchWord in frenchWords:
            numsFromFrench += [text2num(frenchWord, lang='fr', relaxed=True)]

        units = [num for num in range(2, 10)]

        # Number analysis: 
        #        Hundreds
        for i in range(len(numsFromFrench) - 1):
            if (i + 1) <= (len(numsFromFrench) - 1):
                if numsFromFrench[i] in units and numsFromFrench[i + 1] == 100: 
                    numsFromFrench[i] *= numsFromFrench[i + 1]
                    del numsFromFrench[i + 1]

        # 2 * 40
        for i in range(len(numsFromFrench) - 1):
            if (i + 1) <= (len(numsFromFrench) - 1):
                if numsFromFrench[i] == 4 and numsFromFrench[i + 1] == 20: 
                    numsFromFrench[i] *= numsFromFrench[i + 1]
                    del numsFromFrench[i + 1]

        # 17-19
        for i in range(len(numsFromFrench) - 1):
            if (i + 1) <= (len(numsFromFrench) - 1):
                if numsFromFrench[i] == 10 and numsFromFrench[i + 1] in [7, 8, 9]:
                    numsFromFrench[i] += numsFromFrench[i + 1]
                    del numsFromFrench[i + 1]

        tenToEleven = [num for num in range(10, 20)]

        #       Dozens
        for i in range(0, len(numsFromFrench) - 1):
            if (i + 1) <= (len(numsFromFrench) - 1):
                if (numsFromFrench[i] == 60 or numsFromFrench[i] == 80) and (numsFromFrench[i + 1] in tenToEleven or numsFromFrench[i + 1] in units): 
                    numsFromFrench[i] += numsFromFrench[i + 1]
                    del numsFromFrench[i + 1]
                    
        for i in range(numsFromFrench.__len__() - 1):
            status = self.__CheckNumberStatus(numsFromFrench[i], numsFromFrench[i + 1])
            if status != 'OK': 
                return status
        
        self.__ANALYZED_NUMBERS = numsFromFrench

        return 'OK'

    def __LowercaseFirstLetters(self, words: str) -> str:
        
        lowercaseFirstLetter = lambda string: string[:1].lower() + string[1:] if type(string) == str else string

        result = ''
        for word in words.split():
            result += ' ' + lowercaseFirstLetter(word)

        return result[1:]

    def TranslateFromFrenchToArabicAndRomanNumber(self) -> None:

        frenchNumber = self.__LowercaseFirstLetters(self.inputLineEdit.text())

        logOutput = self.__NumberAnalysis(frenchNumber) 

        if logOutput == 'OK':
            frenchNumber = ' '.join([str(num2words(num, lang='fr')) for num in self.__ANALYZED_NUMBERS])
            resultNum = text2num(frenchNumber, "fr", relaxed=True)
            self.resultArabic.setText(str(resultNum)) 
            self.resultRoman.setText(roman.toRoman(resultNum))
        else: 
            msgBox = QMessageBox()
            msgBox.setWindowTitle("Ошибка")
            msgBox.setText(logOutput)
            msgBox.exec()

    __ANALYZED_NUMBERS = []


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main = MainWindow()
    main.setWindowTitle("French words translation")
    main.show()
    sys.exit(app.exec())