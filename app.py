#!/usr/bin/env python3

import re
import sys
from typing import Any, List, Tuple, Union
from abc import ABC, abstractmethod

class AbstractCronExpression(ABC):
    def __init__(self, expression: str):
        parts = expression.split()
        if len(parts) < 6:
            raise ValueError("Invalid cron expression format. Expected at least 6 parts.")
        
        self.raw_minute = parts[0]
        self.raw_hour = parts[1]
        self.raw_day_of_month = parts[2]
        self.raw_month = parts[3]
        self.raw_day_of_week = parts[4]
        self.command = " ".join(parts[5:])
        
    @property
    @abstractmethod
    def minute(self):
        pass
    
    @property
    @abstractmethod
    def hour(self):
        pass
    
    @property
    @abstractmethod
    def day_of_month(self):
        pass
    
    @property
    @abstractmethod
    def month(self):
        pass
    
    @property
    @abstractmethod
    def day_of_week(self):
        pass
    
    def to_table_format(self) -> List[Tuple[str, Union[str, List[Any]]]]:
        return [
            ("minute", self.minute),
            ("hour", self.hour),
            ("day of month", self.day_of_month),
            ("month", self.month),
            ("day of week", self.day_of_week),
            ("command", self.command)
        ]

class RawCronExpression(AbstractCronExpression):
    @property
    def minute(self):
        return self.raw_minute
    
    @property
    def hour(self):
        return self.raw_hour
    
    @property
    def day_of_month(self):
        return self.raw_day_of_month
    
    @property
    def month(self):
        return self.raw_month
    
    @property
    def day_of_week(self):
        return self.raw_day_of_week
    
    def expand(self):
        return CronExpression(
            f"{self.minute} {self.hour} {self.day_of_month} {self.month} {self.day_of_week} {self.command}"
        )
    
    
        
class CronExpression(AbstractCronExpression):
    def __init__(self, expression: str):
        super().__init__(expression)
        
        self._minute = expand_expression(self.raw_minute, list(range(60)))
        self._hour = expand_expression(self.raw_hour, list(range(24)))
        self._day_of_month = expand_expression(self.raw_day_of_month, list(range(1, 32)))
        self._month = expand_expression(self.raw_month, list(range(1, 13)))
        self._day_of_week = expand_expression(self.raw_day_of_week, list(range(1, 8)))
    
    @property
    def minute(self):
        return self._minute
    
    @property
    def hour(self):
        return self._hour
    
    @property
    def day_of_month(self):
        return self._day_of_month
    
    @property
    def month(self):
        return self._month
    
    @property
    def day_of_week(self):
        return self._day_of_week
        

def expand_expression(expression: str, options: List[int]) -> List[int]:
    
    if expression == "*":
        return options

    
    dash_matches = re.search(r"^(\d{1,2})-(\d{1,2})$", expression)
    if dash_matches:
        start, end = int(dash_matches.group(1)), int(dash_matches.group(2))
        if start > end:
            raise ValueError(f"Invalid range in expression: {expression}")
        return [x for x in options if start <= x <= end]
    
    if re.match(r"^\d{1,2}(?:,\d{1,2})*$", expression):
        values = [int(x) for x in expression.split(",")]
        # print(values)
        res_val = [x for x in values if x in options]
        if res_val:
            return res_val
        else:
            raise ValueError(f"Value {values} not in valid options for this component")
    
    interval_matches = re.search(r"^(\*|\d{1,2}-\d{1,2})/(\d{1,2})$", expression)
    
    if interval_matches:
        base_expression = interval_matches.group(1)
        interval = int(interval_matches.group(2))
        if interval <= 0:
            raise ValueError(f"Invalid interval in expression: {expression}")
        
        new_options = expand_expression(base_expression, options)
        # return new_options[::interval]
        return [x for x in new_options if (x - new_options[0]) % interval == 0]
    
    if re.match(r"^\d{1,2}$", expression):
        value = int(expression)
        if value in options:
            return [value]
        else:
            raise ValueError(f"Value {value} not in valid options for this component")
    
    
    raise ValueError(f"unrecognized expression format: {expression}")


class TableOutput:
    def __init__(
        self,
        table_data: List[Tuple[str, Union[str, List[int]]]],
        name_col_length: int = 14
    ):
        self.table_data = table_data
        self.name_col_length = name_col_length
    
    def render(self) -> str:
        out = ""
        for name, value in self.table_data:
            if isinstance(value, list):
                value = " ".join([str(x) for x in value])
            row = f"{self._generate_buffered_col(name, self.name_col_length)} {value}\n"
            out += row
        return out.rstrip()
    
    def _generate_buffered_col(self, name: str, length: int) -> str:
        """Generate a column with padding."""
        return name + " " * (length - len(name))


def expand_cron_exp(cron_exp: str) -> str:
    table_data = RawCronExpression(cron_exp).expand().to_table_format()
    return TableOutput(table_data).render()

def main():
    if len(sys.argv) != 2:
        print("Usage: python3 app.py <cron_expression>")
        sys.exit(1)
    
    try:
        cron_expression = sys.argv[1]
        result = expand_cron_exp(cron_expression)
        print(result)
    except Exception as e:
       print(f"Error: {e}")
       sys.exit(1)
       
       
if __name__ == "__main__":
    main()