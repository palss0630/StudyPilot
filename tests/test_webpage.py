from src.studypilot.tools.webpage import read_webpage, check_ssrf

def test_webpage_reject_localhost():
    assert "Error" in read_webpage("http://localhost:8080")
    assert "Error" in read_webpage("http://127.0.0.1")

def test_webpage_reject_private_ips():
    assert "Error" in read_webpage("http://10.0.0.1")
    assert "Error" in read_webpage("http://192.168.1.1")
    assert "Error" in read_webpage("http://172.16.0.1")

def test_webpage_reject_non_http():
    assert "Error" in read_webpage("ftp://example.com")
    assert "Error" in read_webpage("file:///etc/passwd")

def test_webpage_accept_valid_urls():
    # Test just the validation logic for a valid URL
    try:
        check_ssrf("http://example.com")
        check_ssrf("https://www.google.com")
    except Exception as e:
        assert False, f"Valid URL raised exception: {e}"
