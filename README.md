# conversion
## Конфигурационное управление. Домашняя работа

Вариант 24

Инструмент командной строки для преобразования текста на учебном конфигурационном языке в XML-формат. Реализация включает полный парсер языка с проверкой синтаксиса, вычислением выражений и генерацией структурированного XML.

Требования к языку:

- Однострочные комментарии: % Это комментарий
- Числа: Поддержка целых, дробных и экспоненциальных чисел
- Массивы: [значение значение ...]
- Имена переменных: [_a-zA-Z]+ (латинские буквы и подчеркивание)
- Строки: 'текст в кавычках'
- Объявление констант: global имя = значение
- Выражения: Инфиксные ${a + b * sqrt(c)}
- Операции: +, -, *, /, sqrt(), max()

Функциональность:
1) Чтение из файла (параметр --input)
2) Вывод XML в стандартный поток
3) Детектирование синтаксических ошибок
4) Вычисление константных выражений

Использование:
Используем команду “—input” и укажем пример описания конфигурации:
![Uploading image.png…]()

Пример входного файла:
% Server settings
global port = 8080
global hostname = 'localhost'
global timeout = 30.5
global retries = 3
global settings = [port, hostname, timeout]
global max_connections = ${port * 10}
global optimal_timeout = ${timeout * 2 - 5}

Пример вывода XML:
<?xml version="1.0" ?>
<configuration>
  <constant name="port" type="number">8080</constant>
  <constant name="hostname" type="string">localhost</constant>
  <constant name="timeout" type="number">30.5</constant>
  <constant name="retries" type="number">3</constant>
  <constant name="settings">
    <array>
      <item type="number">8080</item>
      <item type="string">localhost</item>
      <item type="number">30.5</item>
    </array>
  </constant>
  <constant name="max_connections" type="number">80800</constant>
  <constant name="optimal_timeout" type="number">-91.5</constant>
</configuration>
