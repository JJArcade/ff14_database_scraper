import urwid, os, re
##IMPORT RECIPE TOOL
import sys
include_path = os.path.expanduser('~')
include_path = os.path.join(include_path, "Documents", 
       "code_projects", "ff14_database_scraper", "src")
print(include_path)
sys.path.insert(0, include_path)
from recipe_calculator import recipe_calculator as rc

print("HELLO WORLD")
