import subprocess
import re
import time
from prometheus_client import start_http_server, Summary, Gauge


up_days_g           = Gauge('uptime_days', 'Uptime of node in days')
users_g             = Gauge('logged_in_users', 'Count of users logged in')
avg_load_1_min_g    = Gauge('avg_load_1_min', 'Average load over 1 min')
avg_load_5min_g     = Gauge('avg_load_5_min', 'Average load over 5 min')
avg_load_15min_g    = Gauge('avg_load_15_min', 'Average load over 15 min')

tasks_total_g       = Gauge('tasks_total', 'Total amount of tasks')
tasks_running_g     = Gauge('tasks_running', 'Total amount of tasks running')
tasks_sleeping_g    = Gauge('tasks_sleeping', 'Total amount of tasks sleeping')
tasks_stopped_g     = Gauge('tasks_stopped', 'Total amount of tasks stopped')
tasks_zombie_g      = Gauge('tasks_zombie', 'Total amount of task zombies')

cpu_usage_user_g    = Gauge('cpu_usage_user', 'Cpu usage in % of users')
cpu_usage_system_g  = Gauge('cpu_usage_system', 'Cpu usage in % of system')
cpu_usage_low_prio_g= Gauge('cpu_usage_low_prio', 'Cpu usage in % low prio')
cpu_usage_idle_g    = Gauge('cpu_usage_idle', 'Cpu usage in % in idle')
cpu_usage_io_wait_g = Gauge('cpu_usage_io_wait', 'Cpu usage in % in io waits')
cpu_usage_hw_int_g  = Gauge('cpu_usage_hw_int', 'Cpu usage in % hardware interrupts')
cpu_usage_soft_int_g= Gauge('pu_usage_soft_int', 'Cpu usage in % in software interrupts')
cpu_usage_steal_g   = Gauge('cpu_usage_steal', 'Cpu usage in % in steal')

mem_total           = Gauge('mem_total', 'Total memory in MB')
mem_free            = Gauge('mem_free', 'Free memory in MB')
mem_used            = Gauge('mem_used', 'Used memory in MB')
mem_buff_cache      = Gauge('mem_buff_cache', 'Buffer cahce memory in MB')

swap_total          = Gauge('swap_total', 'Total swap memory')
swap_free           = Gauge('swap_free', 'Free swap memory')
swap_used           = Gauge('swap_used', 'Used swap memory')
swap_avail          = Gauge('swap_avail', 'Available swap memory')

gen_info_regex  = re.compile('up\s(\d+)\s.*?(\d+)[:](\d+).*?(\d+)\suser.*?load average[:]\s(\d+,\d+),\s(\d+,\d+),\s(\d+,\d+)')
tasks_regex     = re.compile('Tasks:\s(\d+)\stotal.*?(\d+)\srunning.*?(\d+)\ssleeping.*?(\d+)\sstopped.*?(\d+)\szombie')
cpu_regex       = re.compile('%Cpu.*?(\d+,\d+).*?(\d+,\d+).*?(\d+,\d+).*?(\d+,\d+).*?(\d+,\d+).*?(\d+,\d+).*?(\d+,\d+).*?(\d+,\d+)')
memory_regex    = re.compile('Mi.*?(\d+,\d+).*?(\d+,\d+).*?(\d+,\d+).*?(\d+,\d+)')
swap_regex      = re.compile('Mi.*?(\d+,\d+).*?(\d+,\d+).*?(\d+,\d+).*?(\d+,\d+)')

def gen_metrics():
    p = subprocess.Popen(('top', '-b','-n', '1'), stdout=subprocess.PIPE)
    text = p.communicate()[0].decode()
    # print(text)

    split = text.split('\n')

    gen_matches     = re.search(gen_info_regex, split[0])
    tasks_matches   = re.search(tasks_regex, split[1])
    cpu_matches     = re.search(cpu_regex,split[2])
    mem_matches     = re.search(memory_regex, split[3])
    swap_matches    = re.search(swap_regex, split[4])

    gen_matches     = [val.replace(',','.') for val in gen_matches.groups()]
    tasks_matches   = [val.replace(',','.') for val in tasks_matches.groups()]
    cpu_matches     = [val.replace(',','.') for val in cpu_matches.groups()]
    mem_matches     = [val.replace(',','.') for val in mem_matches.groups()]
    swap_matches    = [val.replace(',','.') for val in swap_matches.groups()]

    up_days, up_hours, up_minutes, users, avg_load_1_min, avg_load_5min, avg_load_15min = gen_matches
    tasks_total, tasks_running, tasks_sleeping, tasks_stopped, tasks_zombie = tasks_matches
    cpu_usage_user, cpu_usage_system, cpu_usage_low_prio, cpu_usage_idle, cpu_usage_io_wait, cpu_usage_hw_int, cpu_usage_soft_int, cpu_usage_steal = cpu_matches
    mem_total, mem_free, mem_used, mem_buff_cache = mem_matches
    swap_total, swap_free, swap_used, swap_available_mem = swap_matches

    # assert re.search('(\s*?PID\s*?USER\s*?PR\s*?NI\s*?VIRT\s*?RES\s*?SHR\s*?S\s*?%CPU\s*?%MEM\s*?TIME[+]\s*?COMMAND)', split[6])

    def get_process_line(line):
        matches = re.search('\s+(\d+)\s+([a-z0-9]+)\s+(\d+)\s+([-]?\d+)\s+(\d+,?\d+?\w?)\s+(\d+)\s+(\d+)\s+(\w)\s+(\d+,\d)\s+(\d+,\d+)\s+(\d+[:]\d+.\d+)\s+([a-z0-9/_]+)', line)
        pid, user, pr, ni, virt, res, shr, s, cpu, mem, time, command = matches.groups()

if __name__ == '__main__':
    # Start up the server to expose the metrics.
    start_http_server(8000)
    # Generate some requests.
    while True:
        gen_metrics()
        time.sleep(5)