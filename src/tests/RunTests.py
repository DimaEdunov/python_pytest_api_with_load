# This class will make our lives easier once running test suites
import os

from src.flow_constructors import domains

"""Run tests """
# Insert 'from' and 'to' in a dictionary form (i.e. : from = (2021,12,1,18,1,5), which is year,month,date,hour,minute
## For parallel run, add : --dist=loadfile -n=1

suite = "dev"
domain = "llfl"
attraction = "cc"
opsui_site_code = domains.get_site_code(domain)

os.system(f'pytest -v -s --alluredir="C:\AllureReports\Data" --html=report.html --self-contained-html -m={suite} --env=se1 --domain={domain} --attraction={attraction} --site_code={opsui_site_code} --from_to_api_time_buffer_seconds=130 --wait_between_cycles_seconds=35 --headless=False')


# Load Testing lunch code
# os.system(f'pytest -v -s -k "test_media_load_japan" -n 30')


# Cycle time calculation breakdown:
# - Connector upload process : 35 seconds
# - Get Media API : insignificant
# - Associate Media API : insignificant
# - Video Creation time : 0.5 minutes (???)
# --dist=loadfile -n=2
"            //EFBV-Camera6-0-20220127085538-motion.mp4"