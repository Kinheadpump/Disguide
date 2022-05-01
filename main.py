import logging
import os
import sys
import urllib3

from src.fetch import Fetch
from src.terminal import Terminal

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

application_path = os.path.dirname(sys.executable)

try:
    os.mkdir(application_path + "\\logs")
except FileExistsError:
    pass

try:
    os.mkdir(application_path + "\\config")
except FileExistsError:
    pass

current_file_nr = len(os.listdir(f'{application_path}\\logs'))
logging.basicConfig(filename=f"{application_path}\\logs\\ValPalLog-{current_file_nr}.txt",
                    filemode='a',
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.DEBUG)
logger = logging.getLogger(f"ValPalLog")

try:
    fetcher = Fetch(logger)
    tml = Terminal(fetcher, logger, application_path)

    tml.cmdloop()
except Exception as e:
    logger.error(f"Had to exit program because of exception {e}")
    sys.exit()
