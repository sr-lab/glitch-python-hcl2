""" Test parsing a variety of hcl files"""
import json
from pathlib import Path
from unittest import TestCase

import hcl2
from hcl2.parser import PARSER_FILE, create_parser_file


HELPERS_DIR = Path(__file__).absolute().parent.parent / "helpers"
HCL2_DIR = HELPERS_DIR / "terraform-config"
JSON_DIR = HELPERS_DIR / "terraform-config-json"
HCL2_FILES = [str(file.relative_to(HCL2_DIR)) for file in HCL2_DIR.iterdir()]


class TestLoad(TestCase):
    """Test parsing a variety of hcl files"""

    def test_load_terraform(self):
        """Test parsing a set of hcl2 files and force recreating the parser file"""
        parser_file = Path(hcl2.__file__).absolute().parent / PARSER_FILE
        parser_file.unlink()
        create_parser_file()
        for hcl_path in HCL2_FILES:
            yield self.check_terraform, hcl_path

    def test_load_terraform_from_cache(self):
        """Test parsing a set of hcl2 files from a cached parser file"""
        for hcl_path in HCL2_FILES:
            yield self.check_terraform, hcl_path

    def check_terraform(self, hcl_path_str: str):
        """Loads a single hcl2 file, parses it and compares with the expected json"""
        hcl_path = (HCL2_DIR / hcl_path_str).absolute()
        json_path = JSON_DIR / hcl_path.relative_to(HCL2_DIR).with_suffix(".json")
        if not json_path.exists():
            assert False, f"Expected json equivalent of the hcl file doesn't exist {json_path}"

        with hcl_path.open("r") as hcl_file, json_path.open("r") as json_file:
            try:
                hcl2_dict = hcl2.load(hcl_file)
            except Exception as exc:
                assert False, f"failed to tokenize terraform in `{hcl_path_str}`: {exc}"

            json_dict = json.load(json_file)
            self.assertDictEqual(hcl2_dict, json_dict, f"failed comparing {hcl_path_str}")
