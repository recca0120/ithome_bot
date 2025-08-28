## 前言

在軟體開發中，如何確保程式碼的穩定性？如何在重構時不破壞既有功能？答案就是：**測試驅動開發（TDD）**！

Python 配合 pytest 測試框架，能讓我們寫出優雅且易讀的測試。在接下來的 30 天，我們將從零開始，學習如何用 TDD 方法開發高品質的 Python 應用。今天，讓我們從環境設置開始，踏出 TDD 的第一步！

## 學習目標

- 建立 Python 專案環境
- 安裝並設定 pytest 測試框架
- 撰寫第一個測試
- 實作簡單的數學函數

## 專案設置

### 1. 建立專案

```bash
mkdir python-tdd
cd python-tdd

# 建立專案結構
mkdir -p src/utilities tests/day01
touch src/__init__.py src/utilities/__init__.py
```

### 2. 設置虛擬環境

```bash
# 建立虛擬環境
python -m venv venv

# 啟動虛擬環境
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

### 3. 安裝測試套件

建立 `requirements.txt`：

```txt
pytest==8.3.3
pytest-cov==5.0.0
pytest-mock==3.14.0
```

安裝套件：

```bash
pip install -r requirements.txt
```

### 4. 設定 pytest

建立 `pytest.ini`：

```ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    -v
    --tb=short
    --cov=src
    --cov-report=term-missing
```

## 第一個測試

### 建立數學函數模組

建立 `src/utilities/math.py`：

```python
"""數學運算函數"""


def add(a: float, b: float) -> float:
    """兩數相加"""
    return a + b


def subtract(a: float, b: float) -> float:
    """兩數相減"""
    return a - b


def multiply(a: float, b: float) -> float:
    """兩數相乘"""
    return a * b


def divide(a: float, b: float) -> float:
    """兩數相除"""
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b
```

### 撰寫測試

建立 `tests/day01/test_math.py`：

```python
"""Day 01: 數學函數測試"""

import pytest
from src.utilities.math import add, subtract, multiply, divide


def test_add_two_positive_numbers():
    """測試兩個正數相加"""
    assert add(2, 3) == 5


def test_add_negative_numbers():
    """測試負數相加"""
    assert add(-2, -3) == -5


def test_add_zero():
    """測試加零"""
    assert add(5, 0) == 5
    assert add(0, 5) == 5


def test_subtract_two_numbers():
    """測試兩數相減"""
    assert subtract(5, 3) == 2


def test_subtract_negative_result():
    """測試負數結果"""
    assert subtract(3, 5) == -2


def test_multiply_two_numbers():
    """測試兩數相乘"""
    assert multiply(3, 4) == 12


def test_multiply_by_zero():
    """測試乘以零"""
    assert multiply(5, 0) == 0


def test_divide_two_numbers():
    """測試兩數相除"""
    assert divide(10, 2) == 5


def test_divide_decimal_result():
    """測試小數結果"""
    assert divide(7, 2) == 3.5


def test_divide_by_zero_raises_error():
    """測試除以零拋出錯誤"""
    with pytest.raises(ValueError, match="Cannot divide by zero"):
        divide(10, 0)
```

## 執行測試

```bash
pytest tests/day01
```

預期輸出：
```
============================= test session starts ==============================
platform darwin -- Python 3.12.4, pytest-8.4.1, pluggy-1.6.0
rootdir: /Users/user/Sites/ithome2025/projects/python
configfile: pytest.ini
collected 10 items

tests/day01/test_math.py::test_add_two_positive_numbers PASSED           [ 10%]
tests/day01/test_math.py::test_add_negative_numbers PASSED               [ 20%]
tests/day01/test_math.py::test_add_zero PASSED                           [ 30%]
tests/day01/test_math.py::test_subtract_two_numbers PASSED               [ 40%]
tests/day01/test_math.py::test_subtract_negative_result PASSED           [ 50%]
tests/day01/test_math.py::test_multiply_two_numbers PASSED               [ 60%]
tests/day01/test_math.py::test_multiply_by_zero PASSED                   [ 70%]
tests/day01/test_math.py::test_divide_two_numbers PASSED                 [ 80%]
tests/day01/test_math.py::test_divide_decimal_result PASSED              [ 90%]
tests/day01/test_math.py::test_divide_by_zero_raises_error PASSED        [100%]

============================== 10 passed in 0.02s ==============================
```

## 測試解析

### 測試結構

```python
def test_something():
    # Arrange - 準備
    a = 2
    b = 3
    
    # Act - 執行
    result = add(a, b)
    
    # Assert - 斷言
    assert result == 5
```

### 常用斷言方法

- `assert x == y`: 檢查相等
- `assert x != y`: 檢查不相等
- `assert x is True`: 檢查為 True
- `assert x is False`: 檢查為 False
- `with pytest.raises(Exception)`: 檢查是否拋出異常

## pytest 特色

1. **簡潔語法**: 使用原生 assert 語句
2. **豐富的 fixtures**: 優雅的測試資料管理
3. **強大的插件生態**: 擴展性強
4. **詳細的錯誤報告**: 快速定位問題

### pytest vs unittest 語法比較

**unittest 風格**：
```python
import unittest

class TestMath(unittest.TestCase):
    def test_add(self):
        self.assertEqual(add(2, 3), 5)
```

**pytest 風格**：
```python
def test_add():
    assert add(2, 3) == 5
```

## 重點整理

1. **環境設置**: Python + pytest 提供強大的測試環境
2. **第一個測試**: 從簡單的純 Python 函數開始
3. **測試結構**: 使用類別組織測試
4. **斷言方法**: assert 配合各種條件判斷

## 練習題

試著為以下函數撰寫測試：

1. `is_even(n)`: 判斷數字是否為偶數
2. `factorial(n)`: 計算階乘
3. `is_prime(n)`: 判斷是否為質數

提示：先寫測試，再實作函數！

## 今日回顧

今天我們成功完成了：
- ✅ 建立 Python 專案環境
- ✅ 安裝並設定 pytest 測試框架
- ✅ 撰寫第一個 pytest 測試
- ✅ 實作並測試數學函數
- ✅ 體驗 pytest 簡潔的語法

## 明日預告

明天是【Day 02】，我們將深入 TDD 的核心 - **Red-Green-Refactor 循環**。透過實作字串處理功能，你將學會：
- 測試優先的思維模式
- 如何實踐 Red-Green-Refactor
- pytest 測試的組織技巧
- 更多實用的斷言方法

讓我們一起在 TDD 的道路上前進！

---

### 專案結構

```
python-tdd/
├── src/
│   ├── __init__.py
│   └── utilities/
│       ├── __init__.py
│       └── math.py
├── tests/
│   └── day01/
│       └── test_math.py
├── pytest.ini
├── requirements.txt
└── venv/
```

### 測試指令

```bash
# 執行所有測試
pytest

# 執行特定檔案
pytest tests/day01/test_math.py

# 執行特定資料夾
pytest tests/day01

# 顯示測試覆蓋率
pytest --cov=src --cov-report=term-missing

# 顯示詳細資訊
pytest -v
```

## 系列文章導航

- 本篇：**Day 01 - 環境設置與第一個測試**
- 下一篇：[Day 02 - Red-Green-Refactor 循環](https://ithelp.ithome.com.tw/articles/10376189)

歡迎留言交流你的測試經驗！如果有任何問題，也歡迎在下方討論。讓我們一起成為更好的開發者！

Happy Testing with pytest! 🐍