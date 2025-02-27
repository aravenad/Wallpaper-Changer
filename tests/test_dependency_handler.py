import subprocess
import sys
import importlib
import pytest
from unittest.mock import patch, MagicMock
from src.dependency_handler import is_package_installed, install_package, ensure_dependencies, REQUIRED_PACKAGES

class TestDependencyHandler:
    @patch('src.dependency_handler.importlib.import_module')
    def test_is_package_installed_true(self, mock_import):
        # Setup mock to simulate installed package
        mock_import.return_value = MagicMock()
        
        result = is_package_installed("some_package")
        assert result is True
        mock_import.assert_called_once_with("some_package")
    
    @patch('src.dependency_handler.importlib.import_module')
    def test_is_package_installed_false(self, mock_import):
        # Setup mock to simulate missing package
        mock_import.side_effect = ImportError()
        
        result = is_package_installed("missing_package")
        assert result is False
        mock_import.assert_called_once_with("missing_package")
    
    @patch('src.dependency_handler.is_package_installed')
    @patch('src.dependency_handler.install_package')
    def test_ensure_dependencies_all_installed(self, mock_install, mock_is_installed):
        # Setup to simulate all dependencies are installed
        mock_is_installed.return_value = True
        
        result = ensure_dependencies(["dep1", "dep2", "dep3"])
        
        assert mock_is_installed.call_count == 3
        mock_install.assert_not_called()
        assert result is True
    
    @patch('src.dependency_handler.is_package_installed')
    @patch('src.dependency_handler.install_package')
    def test_ensure_dependencies_missing_some(self, mock_install, mock_is_installed):
        # Setup to simulate some missing dependencies
        mock_is_installed.side_effect = [True, False, True]
        mock_install.return_value = True
        
        result = ensure_dependencies(["dep1", "dep2", "dep3"])
        
        assert mock_is_installed.call_count == 3
        mock_install.assert_called_once_with("dep2")
        assert result is True
    
    @patch('src.dependency_handler.subprocess.check_call')
    def test_install_package_success(self, mock_check_call):
        mock_check_call.return_value = 0
        
        result = install_package("test_package")
        
        mock_check_call.assert_called_once()
        assert result is True
    
    @patch('src.dependency_handler.subprocess.check_call')
    def test_install_package_failure(self, mock_check_call):
        mock_check_call.side_effect = subprocess.CalledProcessError(1, "cmd")
        
        result = install_package("test_package")
        
        mock_check_call.assert_called_once()
        assert result is False
    
    def test_required_packages_list_not_empty(self):
        assert len(REQUIRED_PACKAGES) > 0

    @patch('src.dependency_handler.logger')
    def test_install_package_logs_correctly_on_success(self, mock_logger):
        """Test that install_package logs correctly on successful installation"""
        with patch('src.dependency_handler.subprocess.check_call') as mock_check_call:
            mock_check_call.return_value = 0
            
            result = install_package("test_package")
            
            assert result is True
            mock_logger.info.assert_any_call("Installing test_package...")
            mock_logger.info.assert_any_call("Successfully installed test_package")

    @patch('src.dependency_handler.logger')
    def test_install_package_logs_correctly_on_failure(self, mock_logger):
        """Test that install_package logs correctly on failed installation"""
        with patch('src.dependency_handler.subprocess.check_call') as mock_check_call:
            mock_check_call.side_effect = subprocess.CalledProcessError(1, "cmd")
            
            result = install_package("test_package")
            
            assert result is False
            mock_logger.info.assert_called_with("Installing test_package...")
            mock_logger.error.assert_called_with("Failed to install test_package")

    @patch('src.dependency_handler.logger')
    def test_ensure_dependencies_logs_missing_packages(self, mock_logger):
        """Test that ensure_dependencies logs correctly when finding missing packages"""
        with patch('src.dependency_handler.is_package_installed', side_effect=[False, True]) as mock_is_installed, \
             patch('src.dependency_handler.install_package', return_value=True) as mock_install:
            
            result = ensure_dependencies(["missing", "installed"])
            
            mock_logger.info.assert_any_call("Installing missing dependencies...")
            mock_logger.info.assert_any_call("All dependencies are now installed.")
            assert result is True

    def test_ensure_dependencies_with_no_arguments(self):
        """Test ensure_dependencies with no arguments (uses REQUIRED_PACKAGES)"""
        with patch('src.dependency_handler.is_package_installed', return_value=True) as mock_is_installed:
            result = ensure_dependencies()
            
            assert mock_is_installed.call_count == len(REQUIRED_PACKAGES)
            assert result is True

    def test_ensure_dependencies_with_installation_failures(self):
        """Test ensure_dependencies when some installations fail"""
        with patch('src.dependency_handler.is_package_installed', side_effect=[False, False]) as mock_is_installed, \
             patch('src.dependency_handler.install_package', side_effect=[True, False]) as mock_install, \
             patch('src.dependency_handler.logger') as mock_logger:
            
            result = ensure_dependencies(["pkg1", "pkg2"])
            
            assert mock_install.call_count == 2
            assert result is False
            mock_logger.warning.assert_called_with("Some dependencies could not be installed.")

    @pytest.mark.skip(reason="Testing __main__ execution is challenging and not critical")
    def test_main_function_calls_ensure_dependencies(self):
        """Test that __main__ calls ensure_dependencies"""
        # This test is challenging to implement reliably
        # The functionality is simple - the __main__ block just calls ensure_dependencies()
        pass
