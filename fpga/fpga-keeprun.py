# Watch / log result and run queued cmd
# Param
# First: xiangshan path
# Second: result log
# TLDR: python3 fpga-keeprun.py v111 /nfs/home/share/fpga/minicom-output/v111-gcc_166-116.log xsbins50m-bk-md5/gcc_166 116

import os
import time
import sys

current_pos = 0
xs_path = sys.argv[1] # xiangshan edition
result_path = sys.argv[2] # result log
spec = sys.argv[3]
fpga = sys.argv[4]

xs_path = "/nfs/home/share/fpga/bits/"+xs_path
result_path = "/nfs/home/share/fpga/minicom-output/"+result_path
workspace = os.popen("pwd").read().strip()

ssh_prefix = f"ssh zhangzifei@172.28.11.{fpga} \"source ~/.zshrc;"
ssh_suffix = "\""
vivado_cmd = ssh_prefix + f"vivado -mode batch -source /nfs/home/share/fpga/0210xsmini/tcl/onboard-ai1-{fpga}.tcl -tclargs " + xs_path + " /nfs/home/share/fpga/" + spec + "/data.txt" + ssh_suffix
uart_cmd = ssh_prefix + f" python3 {workspace}/uart2cap.py \
    {fpga} /dev/ttyUSB0 115200 {result_path} " + ssh_suffix
kill_uart_cmd = ssh_prefix + f" python3 {workspace}/stop_uart.py" + ssh_suffix
kill_vivado_cmd = ssh_prefix + f"python3 {workspace}/stop_vivado.py" + ssh_suffix

def wait_fpga_finish():
  while(int(os.popen(f"grep -c '======== END ' {result_path}").read()) < current_pos):
    time.sleep(60)
  print("get cmd " + str(current_pos) + " result, run next ('0-0')")


try:
  print("kill existed vivado")
  os.system(kill_vivado_cmd)
  print("kill existed uart")
  os.system(kill_uart_cmd)
  if not os.path.isfile(result_path):
    os.popen(f"touch {result_path}")
  time.sleep(10)
  print("watch uart")
  os.popen(uart_cmd)
  while(True):
    wait_fpga_finish()
    os.system(f"echo run command {current_pos}: " + vivado_cmd)
    os.system("date")
    os.system(vivado_cmd)
    current_pos = current_pos + 1
finally:
  print("kill vivado")
  os.system(kill_vivado_cmd)
  print("kill uart")
  os.system(kill_uart_cmd)
  print("stopped")