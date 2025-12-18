# config_to_xml_v24.py
import re
import sys
import argparse
import math
from xml.etree.ElementTree import Element, SubElement, tostring


class ConfigParserV24:
    def __init__(self, config_text):
        self.config_text = config_text
        self.constants = {}
        
    def parse(self):
        lines = self.config_text.split('\n')
        for line_num, line in enumerate(lines, 1):
            # Удаляем комментарии
            if '%' in line:
                line = line.split('%')[0]
            
            line = line.strip()
            if not line:
                continue
                
            self.parse_line(line, line_num)
    
    def parse_line(self, line, line_num):
        # Проверяем объявление константы: global имя = значение
        match = re.match(r'^global\s+([_a-zA-Z]+)\s*=\s*(.+)$', line)
        if not match:
            raise SyntaxError(f"Line {line_num}: Invalid syntax. Expected 'global name = value'")
        
        name = match.group(1)
        value_expr = match.group(2).strip()
        
        # Убираем точку с запятой если есть
        if value_expr.endswith(';'):
            value_expr = value_expr[:-1].strip()
        
        # Обрабатываем значение
        value = self.evaluate_expression(value_expr)
        self.constants[name] = value
    
    def evaluate_expression(self, expr):
        expr = expr.strip()
        
        # Проверяем константное выражение ${...}
        if expr.startswith('${') and expr.endswith('}'):
            inner = expr[2:-1].strip()
            return self.evaluate_math_expression(inner)
        
        # Проверяем массив [...]
        if expr.startswith('[') and expr.endswith(']'):
            return self.parse_array(expr)
        
        # Проверяем строку '...'
        if expr.startswith("'") and expr.endswith("'"):
            return expr[1:-1]
        
        # Проверяем число
        if self.is_number(expr):
            return self.parse_number(expr)
        
        # Проверяем имя константы
        if expr in self.constants:
            return self.constants[expr]
        
        # Проверяем допустимое имя
        if re.match(r'^[_a-zA-Z]+$', expr):
            raise ValueError(f"Undefined constant: {expr}")
        
        raise SyntaxError(f"Invalid expression: {expr}")
    
    def evaluate_math_expression(self, expr):
        # Поддерживаем функции и операции
        expr = expr.strip()
        
        # Обработка функций sqrt() и max()
        sqrt_match = re.match(r'^sqrt\s*\(\s*(.+?)\s*\)$', expr)
        if sqrt_match:
            arg = self.evaluate_math_expression(sqrt_match.group(1))
            if isinstance(arg, (int, float)) and arg >= 0:
                return math.sqrt(arg)
            else:
                raise ValueError(f"Invalid argument for sqrt: {arg}")
        
        max_match = re.match(r'^max\s*\(\s*(.+?)\s*,\s*(.+?)\s*\)$', expr)
        if max_match:
            arg1 = self.evaluate_math_expression(max_match.group(1))
            arg2 = self.evaluate_math_expression(max_match.group(2))
            if isinstance(arg1, (int, float)) and isinstance(arg2, (int, float)):
                return max(arg1, arg2)
            else:
                raise ValueError(f"Invalid arguments for max: {arg1}, {arg2}")
        
        # Обработка инфиксных операций с учетом приоритета
        # Сначала умножение и деление
        mul_div_pattern = r'(.+?)\s*([*/])\s*(.+)'
        mul_div_match = re.match(mul_div_pattern, expr)
        if mul_div_match:
            left = self.evaluate_math_expression(mul_div_match.group(1).strip())
            op = mul_div_match.group(2)
            right = self.evaluate_math_expression(mul_div_match.group(3).strip())
            
            if not (isinstance(left, (int, float)) and isinstance(right, (int, float))):
                raise ValueError(f"Cannot perform {op} on non-numeric values")
            
            if op == '*':
                return left * right
            elif op == '/':
                if right == 0:
                    raise ValueError("Division by zero")
                return left / right
        
        # Затем сложение и вычитание
        add_sub_pattern = r'(.+?)\s*([+-])\s*(.+)'
        add_sub_match = re.match(add_sub_pattern, expr)
        if add_sub_match:
            left = self.evaluate_math_expression(add_sub_match.group(1).strip())
            op = add_sub_match.group(2)
            right = self.evaluate_math_expression(add_sub_match.group(3).strip())
            
            if not (isinstance(left, (int, float)) and isinstance(right, (int, float))):
                raise ValueError(f"Cannot perform {op} on non-numeric values")
            
            if op == '+':
                return left + right
            elif op == '-':
                return left - right
        
        # Если не операция, то это базовое значение
        return self.evaluate_expression(expr)
    
    def parse_array(self, expr):
        if not expr.startswith('[') or not expr.endswith(']'):
            raise SyntaxError(f"Invalid array syntax: {expr}")
        
        inner = expr[1:-1].strip()
        if not inner:
            return []
        
        items = []
        buffer = ""
        depth = 0
        
        for char in inner:
            if char == ',' and depth == 0:
                if buffer.strip():
                    items.append(self.evaluate_expression(buffer.strip()))
                buffer = ""
            else:
                buffer += char
                if char == '[':
                    depth += 1
                elif char == ']':
                    depth -= 1
        
        if buffer.strip():
            items.append(self.evaluate_expression(buffer.strip()))
        
        return items
    
    def is_number(self, expr):
        # Проверяем соответствие паттерну чисел из ТЗ
        pattern = r'^-?(\d+|\d+\.\d*|\.\d+)([eE][-+]?\d+)?$'
        return bool(re.match(pattern, expr))
    
    def parse_number(self, expr):
        if '.' in expr or 'e' in expr or 'E' in expr:
            return float(expr)
        return int(expr)
    
    def to_xml_string(self):
        root = Element("configuration")
    
        for name, value in self.constants.items():
            const_elem = SubElement(root, "constant")
            const_elem.set("name", name)
        
            if isinstance(value, list):
                array_elem = SubElement(const_elem, "array")
                for item in value:
                    item_elem = SubElement(array_elem, "item")
                    if isinstance(item, str):
                        item_elem.set("type", "string")
                    else:
                        item_elem.set("type", "number")
                    item_elem.text = str(item)
            else:
                const_elem.set("type", "string" if isinstance(value, str) else "number")
                const_elem.text = str(value)
    
        # Форматируем XML с отступами
        from xml.dom import minidom
        rough_string = tostring(root, encoding="unicode")
        reparsed = minidom.parseString(rough_string)
        return reparsed.toprettyxml(indent="  ")


def main():
    parser = argparse.ArgumentParser(description="Convert configuration to XML (Variant 24)")
    parser.add_argument("--input", required=True, help="Path to input configuration file")
    args = parser.parse_args()
    
    try:
        with open(args.input, 'r', encoding='utf-8') as f:
            config_text = f.read()
        
        parser = ConfigParserV24(config_text)
        parser.parse()
        xml_output = parser.to_xml_string()
        
        # Выводим в stdout как требует ТЗ
        print(xml_output)
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()