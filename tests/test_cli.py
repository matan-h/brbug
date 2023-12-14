# this file was written almost entirely by chatGPT.
import os
import tarfile
import pytest
from unittest.mock import patch
from click.testing import CliRunner
from brbug.__main__ import create_tar_from_config, create_tar_gz, get_output_from_source

@pytest.fixture
def runner():
    return CliRunner()

def test_create_tar_gz(tmpdir):
    # Create some test files in a temporary directory
    test_dir = tmpdir.mkdir("test_folder")
    test_file_1 = test_dir.join("test_file_1.py")
    test_file_1.write("# Test file 1")
    test_file_2 = test_dir.join("test_file_2.py")
    test_file_2.write("# Test file 2")

    output_filename = os.path.join(str(tmpdir), "test_output.tar.gz")

    # Call the function
    create_tar_gz(str(test_dir), output_filename)

    # Assert that the tar.gz file is created
    assert os.path.isfile(output_filename)

    # Verify the content of the tar.gz file
    with tarfile.open(output_filename, 'r:gz') as tar:
        member_names = tar.getnames()
        assert 'test_file_1.py' in member_names
        assert 'test_file_2.py' in member_names

def test_get_output_from_source(tmpdir):
    source_folder = str(tmpdir)
    expected_output = os.path.join(source_folder, "resources", "_brbug.tar.gz")

    # Call the function
    output = get_output_from_source(source_folder)

    # Assert that the output matches the expected output filename
    assert output == expected_output

def test_create_tar_from_config_no_args(runner, tmpdir):
    # Change the current working directory to the temporary directory
    os.chdir(str(tmpdir))

    # Call the function without any arguments
    result = runner.invoke(create_tar_from_config)

    # Assert that the function prompts for either a configuration file or a source folder
    assert 'Please provide either a configuration file' in result.output

def test_create_tar_from_config_with_source(runner, tmpdir):
    # Create some test files in a temporary directory
    test_dir = tmpdir.mkdir("test_folder")
    test_file_1 = test_dir.join("test_file_1.py")
    test_file_1.write("# Test file 1")
    test_file_2 = test_dir.join("test_file_2.py")
    test_file_2.write("# Test file 2")

    output_filename = os.path.join(str(tmpdir), "test_output.tar.gz")

    # Call the function with a source folder
    runner.invoke(create_tar_from_config, ['-s', str(test_dir), '-o', output_filename])

    # Assert that the function created a valid tar.gz file from the provided source folder
    assert os.path.isfile(output_filename)
    with tarfile.open(output_filename, 'r:gz') as tar:
        member_names = tar.getnames()
        assert 'test_file_1.py' in member_names
        assert 'test_file_2.py' in member_names

def test_create_tar_from_config_invalid_source(runner, tmpdir):
    # Call the function with a non-existent source folder
    result = runner.invoke(create_tar_from_config, ['-s', 'non_existent_folder'])

    # Assert that the function handles a non-existent source folder gracefully
    assert "Path 'non_existent_folder'" in result.output

# Similar test cases for other scenarios...

def test_create_tar_from_config_run_disabled(runner, tmpdir):
    output_filename = os.path.join(str(tmpdir), "test_output.tar.gz")

    # Call the function with the disable_run flag
    with patch('subprocess.call') as mock_subprocess_call:
        runner.invoke(create_tar_from_config, ['-s', '.', '-o', output_filename, '--disable-run'])

        # Assert that the 'briefcase run' command is not executed
        mock_subprocess_call.assert_not_called()

def test_create_tar_from_config_run_enabled(runner, tmpdir):
    output_filename = os.path.join(str(tmpdir), "test_output.tar.gz")

    # Patch subprocess.call to check if it's called with expected arguments
    with patch('subprocess.call') as mock_subprocess_call:
        # Call the function without the disable_run flag
        runner.invoke(create_tar_from_config, ['-s', '.', '-o', output_filename])

        # Assert that subprocess.call was called with the 'briefcase run' command
        mock_subprocess_call.assert_called_once()

def test_create_tar_from_config_with_config(runner, tmpdir):
    # Create a temporary pyproject.toml file with a 'tool.briefcase.app.*.sources' key
    src_dir = tmpdir.mkdir("src")
    toml_data = f"""
    [tool.briefcase.app.example_app]
    sources = ['{src_dir}']
    """
    config_file = tmpdir.join("pyproject.toml")
    config_file.write(toml_data)

    # Create some test files in a 'src' directory
    test_file_1 = src_dir.join("test_file_1.py")
    test_file_1.write("# Test file 1")
    test_file_2 = src_dir.join("test_file_2.py")
    test_file_2.write("# Test file 2")

    output_filename = os.path.join(str(tmpdir), "test_output.tar.gz")

    # Call the function with the configuration file
    print(['-c', str(config_file), '-o', output_filename])
    result = runner.invoke(create_tar_from_config, ['-c', str(config_file), '-o', output_filename,"--disable-run"])
    print(result)
    # Assert that the function created a valid tar.gz file from the provided source folder in the TOML config
    assert os.path.isfile(output_filename)
    with tarfile.open(output_filename, 'r:gz') as tar:
        member_names = tar.getnames()
        assert 'test_file_1.py' in member_names
        assert 'test_file_2.py' in member_names

def test_create_tar_from_config_invalid_config(runner, tmpdir):
    # Create an invalid pyproject.toml file with missing 'tool.briefcase.app.*.sources' key
    invalid_toml_data = """
    [tool.briefcase.app.example_app]
    # Missing sources key
    """
    invalid_config_file = tmpdir.join("invalid_pyproject.toml")
    invalid_config_file.write(invalid_toml_data)

    # Call the function with the invalid configuration file
    result = runner.invoke(create_tar_from_config, ['-c', str(invalid_config_file)])

    # Assert that the function handles an invalid TOML config file gracefully
    assert 'Invalid configuration file format' in result.output
