from math import sqrt, fabs
import scipy
from scipy import stats
import numpy as np

file = open("transaction.txt", "r")

# загрузим данные из файла в массив строк data_af и data_r соттветственно

data_af = []
data_r = []
for line in file:
    if (line[-1] == "\n"):
        line = line[:-1]
    if "AF" in line:
        data_af += line.split(",")
    else:
        data_r += line.split(",")

# количество клиентов, совершивших транзакции в определенном секторе
# подсчитаем количество уникальных ID, так как некоторые клиенты могли совершать
# транзакции не один раз

def count_unique_ids(data):
    count = 0
    dublicated = []

    for i in range(1, len(data), 4):
        coeff = data.count(data[i])
        if  coeff != 1 and (data[i] not in dublicated):
            count += coeff
            dublicated.append(data[i])
        else:
            count += 1
    return count

count_af = count_unique_ids(data_af)
count_r = count_unique_ids(data_r)

print("Количество клиентов, совершивших транзакции в AF >> ", count_af)
print("Количество клиентов, совершивших транзакции в R >> ", count_r, end="\n\n")

# Средний объем транзакции в определенном секторе
# (математическое ожидание дискретной величины)
# Опеределим как значние / вероятность выпадения этого значения

def expected_value(data):
    num_transactions = len(data) / 4
    expected_value = 0.0

    for i in range(2, len(data), 4):
        count = data.count(data[i])
        p = count / num_transactions
        expected_value = expected_value + p * float(data[i])

    return expected_value

expected_value_af = expected_value(data_af)
expected_value_r = expected_value(data_r)

print("Средний объем транзакции для AF >> {:.2f}".format(expected_value_af))
print("Средний объем транзакции для R >> {:.2f}\n\n".format(expected_value_r))

# Определяем дисперсии величин
def dispersion_value(data, expected_value):
    num_transactions = len(data) / 4
    dispersion_value = 0.0
    expected_value_2 = 0.0

    for i in range(2, len(data), 4):
        p = data.count(data[i]) / num_transactions
        expected_value_2 = expected_value_2 + ((float(data[i]))**2)*p

    dispersion_value = expected_value_2 - expected_value**2

    return dispersion_value

sq_dispersion_value_af = sqrt(dispersion_value(data_af, expected_value_af))
sq_dispersion_value_r = sqrt(dispersion_value(data_r, expected_value_r))

# Раскомментировать для вывода таблицы Лапласса
#laplass_table = scipy.stats.norm.cdf(np.linspace(0,4,101)) - 0.5

# Поиск доверительного интервала для математического ожидания (среднее объема)
# при известной дисперсии для распределения дискретного типа
# P = 0.9 = 2Ф(x) => x (из таблицы Лапласса для Ф(x)=0.45) = 0.36
# x = eps * sqrt(n) / sq_dispersion_value => eps = x * sq_dispersion_value / sqrt(n)
x = 0.36

print("90% Доверительный интервал значений для AF [0, {:.2f}]".format(sq_dispersion_value_af * x / sqrt(len(data_af)/4)))
print("90% Доверительный интервал значений для R [0, {:.2f}]".format(sq_dispersion_value_r * x / sqrt(len(data_r)/4)))

# проверка математической гипотезы
# Пусть H0 = {m_r = m_af}, при gamma = 0.1 (уровне значимости = ошибка первого рода)
# H1 = {m_r != m_af}
# Предположим что тестирующая (критическая) статистика имеет нормальное распределение
# значение квантиля - u=1.282 (по таблице квантелей для нормального распределения)
# определяем критическую зону
# w : {|T(X_)| >= u}
# где статистика T(X_) = (m_af - X_) * sqrt(n) / sq_dispersion_value
# X_ - несмещенная оценка мат ожидания - для дискретной величины - среднее арифметическое

def average_and_X(data):
    summ = 0
    for i in range(2, len(data), 4):
        summ = summ + float(data[i])
    return summ / (len(data)/4), summ

average_af, X_af = average_and_X(data_af)
average_r, X_r = average_and_X(data_r)

def theory_h(m, X_, n, sq_dispersion_value, u):
    if fabs((m - X_) * sqrt(n) / (sq_dispersion_value)) >= u:
        return True
    else:
        return False

u_01 = 1.282

result = theory_h(average_af, X_r, len(data_r)/4, sq_dispersion_value_r, u_01)

print( "Гипотеза о равенстве средних объемов", "верна" if (not result) else "неверна" )
