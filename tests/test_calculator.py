from src.studypilot.tools.calculator import calculator

def test_calculator_basic_arithmetic():
    assert calculator("2+2") == "4"
    assert calculator("10*5") == "50"
    assert calculator("100/4") == "25.0"

def test_calculator_math_functions():
    assert calculator("sqrt(16)") == "4.0"
    assert calculator("abs(-5)") == "5"

def test_calculator_constants():
    assert calculator("pi").startswith("3.14")
    assert calculator("e").startswith("2.71")

def test_calculator_security_eval():
    assert "Error" in calculator("__import__('os').system('rm -rf /')")
    assert "Error" in calculator("open('/etc/passwd')")
    assert "Error" in calculator("exec('...')")
    assert "Error" in calculator("compile('...')")
    assert "Error" in calculator("lambda x: x")

def test_calculator_security_large_powers():
    assert "Error" in calculator("1000**1000")

def test_calculator_malformed():
    assert "Error" in calculator("2 + * 2")
