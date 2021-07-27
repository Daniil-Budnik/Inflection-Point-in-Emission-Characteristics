
# Рекомендуется использовать Python 3.7

# Если библиотеки не установлены, НЕОБХОДИМО в консоль прописать следующие команды:
#    pip install matplotlib
#    pip install scipy
#    pip install pandas
#    pip install python-tk
#    pip install console_progressbar

import matplotlib.pyplot as plt                 # Библиотека для графиков
import numpy as np                              # Математическа библиотека
import pandas as pd                             # Работа с файлами
from scipy import interpolate                   # Библиотека с методом интерполяции
from tkinter.filedialog import askdirectory     # Откртие файлов
import os                                       # Работа с системой
from console_progressbar import ProgressBar     # Прогресс бар

# ----------------------------------------------------------------------------------------------------------

# Метод для интерполяции и визуализации данных
#   X,Y     - Входные данные
#   LEN     - Кол-во точек интерполяции
#   TITLE   - Подпись графа
#   NAME    - Имя файла для сохранения PNG картинки графика
#   DISP    - Допустимое отклонение (ЭМПЕРИЧЕСКИ ПОДОБРАННОЕ ЗНАЧЕНИЕ, ИСХОДЯ ИЗ ГРАФИКОВ МОЖНО МЕНЯТЬ)
def MyInflection(X, Y, LEN=100, TITLE="", NAME="I",  DISP = 20):

    # Сообщения для анализа
    Target = True               

    # Метод отсеивания графиков, не подходящих для анализа
    OldY = Y[0]
    for NewY in Y:
        if (NewY < OldY) and (abs(NewY-OldY) > DISP): Target = False
        OldY = NewY

    InX = np.linspace(min(X), max(X), LEN)          # Генерируем ряд, по которому произведём интерполяцию
    Tck = interpolate.splrep(X, Y)                  # Заготовка для интерполяции
    InY = interpolate.splev(InX, Tck)               # Получаем интерполированные данные

    # Если график подходит для анализа
    if(Target):    
        
        # Переходные процентные соотношения
        TargetRedPercent    = 27
        TargetYellowPercent = 8
         
        Len = len(Y)-1                                          # Кол-во точек
        MiddleID = int(len(Y)/2)                                # Точка середины
        H = 0.01                                                # Шаг для построения вспомогатеьных линий

        # Точки для пересечения вспомогательныйх линий
        RedLeftPoint        = 0  
        RedRightPoint       = 0 
        YellowLeftPoint     = MiddleID      
        YellowRightPoint    = MiddleID

        # В процентном соотношении выясняем разницу между соседними точками от начала до середины графика
        FullPercent = (Y[MiddleID] - Y[0]) / 100
        ArrPercent  = [ int(abs(Y[ID]-Y[ID-1])/FullPercent) for ID in range(1, MiddleID) ]

        # Если разница менее какого-то %, значит предыдущая точка будет являться второй точкой пересичения 
        ID = 0
        while(ArrPercent[ID] > TargetRedPercent and ID < len(ArrPercent)-1):
            ID += 1
        RedRightPoint = ID
        
        # В процентном соотношении выясняем разницу между соседними точками от середины графика до конца
        FullPercent = (Y[Len-1] - Y[MiddleID]) / 100
        ArrPercent = [ int(abs(Y[ID]-Y[ID-1])/FullPercent) for ID in range(MiddleID, Len) ]

        # Если разница менее какого-то %, значит предыдущая точка будет являться второй точкой пересичения 
        ID = len(ArrPercent)-1
        while(ArrPercent[ID] > TargetYellowPercent and ID > int(len(ArrPercent)/2)):
            ID -= 1
        YellowRightPoint = MiddleID + ID 

        # Тут мы находим позиции найденых точек на интерполироемом сигнал

        ID = 0
        while(abs(InY[ID] - Y[RedRightPoint]) > 0.5):     ID += 1
        RedLeftPointID = 0
        RedRightPointID = ID

        ID = MiddleID
        while(abs(InY[ID] - Y[YellowLeftPoint]) > 0.1):   ID += 1
        MiddlePointID = ID

        ID = MiddleID
        while(abs(InY[ID] - Y[YellowRightPoint]) > 0.1):  ID += 1
        YellowRightPointID = ID

        # Узнаем шаг между точками
        if(RedRightPointID      -   RedLeftPointID == 0):  RedRightPointID += 1
        StepRed     = abs(InY[RedRightPointID]      -   InY[RedLeftPointID])    / (RedRightPointID      -   RedLeftPointID)
        if(YellowRightPointID   -   MiddlePointID == 0):  YellowRightPointID += 1
        StepYellow  = abs(InY[YellowRightPointID]   -   InY[MiddlePointID])     / (YellowRightPointID   -   MiddlePointID)

        # Создаём массивы для вспомогательных линий 
        Y_Line_1    = [ InY[0] + StepRed * ID  for ID in range(0, len(InY)) ]
        Y_Line_2    = [ InY[MiddlePointID] - StepYellow * (MiddlePointID-ID) for ID in range(0, MiddlePointID) ]
        for ID in range(MiddlePointID, len(InY)): Y_Line_2.append(Y_Line_2[len(Y_Line_2)-1] + StepYellow)
         
        # Точка пересечения
        IRD = np.argwhere(np.diff(np.sign(np.array(Y_Line_1) - np.array(Y_Line_2)))).flatten()[0]
        
        # Вспомогательная переменная для ограничения отрисовки красной линии
        RD = -1 * int((len(InX) - IRD) / 20) * 19                                                
        
        plt.plot(InX[:RD],    Y_Line_1[:RD],   alpha=0.5, color="red",    label="Tangent 0 and 1")      # Рисуем левую красную линию
        plt.plot(InX,    Y_Line_2,   alpha=0.5, color="yellow", label="Tangent N and N/2")              # Рисуем правую желтую линию

        # Проверка на артифакт
        if(ID != -1):
            plt.axvline(InX[IRD],      color='blue',   label='Inflection Point')                         # Выделяем точку пересечения
            plt.xlabel("Точка перегиба: " + str(InX[IRD]))                                               # Вывести точку перегиба
    
    # Вывод сообщения в случае, если график не подходит для анализа 
    else: plt.xlabel("Данный график не подходит для анализа")                                           

    # Построение графов
    plt.title(TITLE)                                                                            # Подпись
    plt.plot(X, Y, "o",         color="magenta",label="Init Data")                              # Рисуем данные точки
    plt.plot(InX, InY,          color="lime",   label="Interpolate")                            # Рисуем интерполяцию
    plt.legend(); plt.grid()                                                                    # Легенда и сетка
    plt.show()                                                                                  # Открытия окна для анализа (если мешает, закомментируйте строку)
    #plt.savefig(str(NAME))                                                                      # Сохраняем картинку результата
    plt.cla(); plt.clf()                                                                        # Очистка для построения следующего графа 

# ----------------------------------------------------------------------------------------------------------

# Тёмная тема 
def DarkGraph():
    plt.rcParams['figure.edgecolor'] = "333333"
    plt.rcParams['figure.facecolor'] = "333333"
    plt.rcParams['figure.figsize'] = 15, 9
    plt.rcParams['text.color'] = "CCCC00"
    plt.rcParams['axes.labelcolor'] = "ffffff"
    plt.rcParams['axes.edgecolor'] = "ffffff"
    plt.rcParams['axes.facecolor'] = "222222"
    plt.rcParams['savefig.edgecolor'] = "222222"
    plt.rcParams['savefig.facecolor'] = "222222"
    plt.rcParams['xtick.color'] = "CCAA00"
    plt.rcParams['ytick.color'] = "CCAA00"
    plt.rcParams['xtick.minor.visible'] = True
    plt.rcParams['ytick.minor.visible'] = True
    plt.rcParams['boxplot.meanline'] = True
    plt.rcParams['figure.frameon'] = False
    plt.rcParams['grid.color'] = "055212"
    plt.rcParams['font.size'] = 12
    plt.grid(True)


def Analysis(PATH, LEN, NAME):

    # Считываем файлы
    print(PATH)
    FILES = pd.read_excel(PATH, sheet_name="Отчет")

    # Получаем данные
    X = [float(FILES['Unnamed: 0'][i]) for i in range(10, len(FILES['Unnamed: 0']))]
    Y = [float(FILES['Unnamed: 1'][i]) for i in range(10, len(FILES['Unnamed: 1']))]

    # Массив по X и по Y, длина ряда для интерполяции, подпись графа
    MyInflection(X, Y, LEN=LEN, TITLE=PATH, NAME=NAME)


# Главный метод
def main():

    DarkGraph() # Тёмная тема

    # Длина ряда для интерполяции
    print("\n\t>>> Нахождение точки перегиба <<<\n")
    print(" >> Путь к папке с файлами excel...")
    # PATH_LOAD = askdirectory()                      # Путь к файлам (конкретная папка с файлами)
    PATH_LOAD = "D:\\Data Science\\Эммисионные характеристики - Алмаз (2021)"
    print(PATH_LOAD + "\n >> Путь для сохранени результатов...")
    # PATH_SAVE = askdirectory()                      # Путь к файлам (конкретная папка с файлами)
    PATH_SAVE = "C:\\Users\\danii\\Desktop"
    LEN = 5000                                      # Кол-во точек интерполяции
    FILE_LIST = []                                  # Список файлов для чтения (EXCEL)
 
    print(PATH_SAVE + "\n >> Чтение файлов:\n")

    #Analysis(PATH_LOAD + "\\10.xlsx", LEN, "D")

    # Получаем все EXCEL файлы
    for root, dirs, files in os.walk(PATH_LOAD):
        for filename in files:
            print("Файл: " + filename)
            FILE_LIST.append(str (PATH_LOAD + "/" + filename) )
    
    # Проходим по всем файлам
    N = 1;                                      
    print("\n >> Начинаем анализ")
    pb = ProgressBar(total=100, prefix='Анализ')                    # Прогресс бар, для того, чтобы оценить сколько будет длится анализ
    for FILE_PATH in FILE_LIST:                                     # Проходим по всем файлам
        Analysis(FILE_PATH, LEN, PATH_SAVE+"/Result"+str(N))        # Начинаем анализ файла
        pb.print_progress_bar((N)/len(FILE_LIST)*100)               # После, обновление прогресс бара
        N += 1                                                      # Счётчик
        
    print("\n\t>>> Завершение <<<\n")



# ----------------------------------------------------------------------------------------------------------
if __name__ == "__main__": main()
# ----------------------------------------------------------------------------------------------------------
