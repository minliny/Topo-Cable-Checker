from src.application.check_run_services.check_run_service import CheckRunService
from src.crosscutting.logging.logger import get_logger

import sys
import logging

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

svc = CheckRunService()
try:
    svc.run_checks("5365aa3e-84fe-4eb1-b2fb-fa195e2af4fd")
except Exception as e:
    import traceback
    traceback.print_exc()
