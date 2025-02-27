from unittest.mock import patch, MagicMock
from src.cli import parse_args

class TestCLIExtended:
    def test_parse_args_category(self):
        with patch('sys.argv', ['script.py', '--category', 'nature']):
            args = parse_args()
            assert args.category == 'nature'
    
    def test_parse_args_search(self):
        with patch('sys.argv', ['script.py', '--search', 'mountain,river']):
            args = parse_args()
            assert args.search == 'mountain,river'

    def test_parse_args_save(self):
        with patch('sys.argv', ['script.py', '--save']):
            args = parse_args()
            assert args.save is True
    
    def test_parse_args_auto_interval(self):
        with patch('sys.argv', ['script.py', '--auto-interval', '60']):
            args = parse_args()
            assert args.auto_interval == 60
    
    def test_parse_args_featured(self):
        with patch('sys.argv', ['script.py', '--featured']):
            args = parse_args()
            assert args.featured is True
    
    def test_parse_args_multiple_args(self):
        with patch('sys.argv', ['script.py', '--category', 'nature', '--save', '--featured']):
            args = parse_args()
            assert args.category == 'nature'
            assert args.save is True
            assert args.featured is True
    
    @patch('src.cli.update_wallpaper')
    def test_run_cli_basic_execution(self, mock_update_wallpaper):
        # Instead of directly calling run_cli which may have complex dependencies,
        # we'll mock all the necessary functions and test the argument parsing logic
        with patch('sys.argv', ['script.py']):
            from src.cli import run_cli
            run_cli()
            mock_update_wallpaper.assert_called_once()
    
    @patch('src.cli.display_categories')
    def test_list_categories_command(self, mock_display_categories):
        with patch('sys.argv', ['script.py', '--list-categories']):
            from src.cli import run_cli
            run_cli()
            mock_display_categories.assert_called_once()
    
    @patch('src.cli.handle_auto_mode')
    def test_auto_mode_command(self, mock_handle_auto_mode):
        with patch('sys.argv', ['script.py', '--auto']):
            from src.cli import run_cli
            run_cli()
            mock_handle_auto_mode.assert_called_once()
