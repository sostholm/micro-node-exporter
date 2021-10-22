import subprocess
import re
import time
from prometheus_client import start_http_server, Summary, Gauge

general_guages = [
    Gauge('uptime_days', 'Uptime of node in days'),
    Gauge('logged_in_users', 'Count of users logged in'),
    Gauge('avg_load_1_min', 'Average load over 1 min'),
    Gauge('avg_load_5_min', 'Average load over 5 min'),
    Gauge('avg_load_15_min', 'Average load over 15 min')
]

tasks_guages = [
    Gauge('tasks_total', 'Total amount of tasks'),
    Gauge('tasks_running', 'Total amount of tasks running'),
    Gauge('tasks_sleeping', 'Total amount of tasks sleeping'),
    Gauge('tasks_stopped', 'Total amount of tasks stopped'),
    Gauge('tasks_zombie', 'Total amount of task zombies')
]

cpu_guages = [
    Gauge('cpu_usage_user', 'Cpu usage in % of users'),
    Gauge('cpu_usage_system', 'Cpu usage in % of system'),
    Gauge('cpu_usage_low_prio', 'Cpu usage in % low prio'),
    Gauge('cpu_usage_idle', 'Cpu usage in % in idle'),
    Gauge('cpu_usage_io_wait', 'Cpu usage in % in io waits'),
    Gauge('cpu_usage_hw_int', 'Cpu usage in % hardware interrupts'),
    Gauge('pu_usage_soft_int', 'Cpu usage in % in software interrupts'),
    Gauge('cpu_usage_steal', 'Cpu usage in % in steal')
]

mem_guages = [
    Gauge('mem_total', 'Total memory in MB'),
    Gauge('mem_free', 'Free memory in MB'),
    Gauge('mem_used', 'Used memory in MB'),
    Gauge('mem_buff_cache', 'Buffer cahce memory in MB')
]

swap_guages = [
    Gauge('swap_total', 'Total swap memory'),
    Gauge('swap_free', 'Free swap memory'),
    Gauge('swap_used', 'Used swap memory'),
    Gauge('swap_avail', 'Available swap memory')
]

gen_info_regex  = 'up\s(\d+)\s.*?(\d+)[:](\d+).*?(\d+)\suser.*?load average[:]\s(\d+,\d+),\s(\d+,\d+),\s(\d+,\d+)'
tasks_regex     = 'Tasks:\s(\d+)\stotal.*?(\d+)\srunning.*?(\d+)\ssleeping.*?(\d+)\sstopped.*?(\d+)\szombie'
cpu_regex       = '%Cpu.*?(\d+,\d+).*?(\d+,\d+).*?(\d+,\d+).*?(\d+,\d+).*?(\d+,\d+).*?(\d+,\d+).*?(\d+,\d+).*?(\d+,\d+)'
memory_regex    = 'Mi.*?(\d+,\d+).*?(\d+,\d+).*?(\d+,\d+).*?(\d+,\d+)'
swap_regex      = 'Mi.*?(\d+,\d+).*?(\d+,\d+).*?(\d+,\d+).*?(\d+,\d+)'

def set_guages(guages, matches):
        for index, guage in enumerate(guages):
            guage.set(matches[index])

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

    set_guages(general_guages, gen_matches)
    set_guages(tasks_guages, tasks_matches)
    set_guages(cpu_guages, cpu_matches)
    set_guages(mem_guages, mem_matches)
    set_guages(swap_guages, swap_matches)

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