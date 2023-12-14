# some functions are written using chatGPT
import tarfile
import pytest
from unittest.mock import patch
from brbug.brbug import (
    catch,
    catch_beeapp,
    friendly_string,
    _friendly_string,
    MySource,
)

def test_friendly_string():
    # Test friendly_string function
    try:
        # Code that raises an exception
        1 / 0
    except Exception as e:
        # Check if the output of friendly_string contains the exception message
        friendly_output = friendly_string(e)
        assert "ZeroDivisionError" in friendly_output
        assert "occurs when" in friendly_output

def test_friendly_string_internal():
    # Test _friendly_string function (internal function)
    output = _friendly_string(ZeroDivisionError, ZeroDivisionError("Test"), None)
    assert "ZeroDivisionError" in output
    assert "occurs when" in output

def test_catch_decorator():
    # Test the behavior of the catch decorator
    @catch
    def func_with_exception():
        1 / 0

    with patch('brbug.brbug.popup_error') as mock_popup_error:
        func_with_exception()
        # Ensure popup_error is called when an exception is caught
        mock_popup_error.assert_called_once()

def test_catch_beeapp_decorator():
    # Test the behavior of catch_beeapp decorator on individual methods
    class OneClass:
        def anerror_without_catch(self):
            return 1 / 0
    
    @catch_beeapp
    class MyClass(OneClass):
        def anerror_with_catch(self):
            return 1 / 0

    # Test method without catch
    obj_with_catch = MyClass()

    with pytest.raises(ZeroDivisionError):
        obj_with_catch.anerror_without_catch()
    
    # Test method with catch
    with patch('brbug.brbug.popup_error') as mock_popup_error:
        obj_with_catch.anerror_with_catch()
        # Ensure popup_error is called when an exception is caught
        mock_popup_error.assert_called_once()

@pytest.fixture
def test_tar_file(tmp_path,monkeypatch):
    # Create a temporary .tar.gz file with test content
    resources = tmp_path / "resources"
    resources.mkdir()

    test_content = b"Test content line 1\nTest content line 2\n"
    test_file_path = "test_file.txt"
    with open(test_file_path, "wb") as file:
        file.write(test_content)
    
    test_tar_path = resources / "_brbug.tar.gz"
    with tarfile.open(test_tar_path, "w:gz") as tar:
        tar.add(test_file_path, arcname="test_file.txt")
    
    monkeypatch.setattr("brbug.brbug.find_app_path", lambda: str(tmp_path))
    return tar.name

def test_MySource_tar_reading(test_tar_file):
    # Initialize MySource with the generated .tar.gz file
    source = MySource("test_file.txt", [])

    # Read the content from the tar file
    assert source.lines != []  # Lines should not be empty if tar content was read
    assert source.lines == ["Test content line 1", "Test content line 2"]