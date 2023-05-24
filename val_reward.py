#!/usr/bin/env python3
#-*-coding:utf8-*-

import os
import re
import sys
import time
import json
import subprocess

recipient_addr='YOUR_ADDR_TO_RECIEVE_SUI'
gas_budget = 20000000

print("1. >> sui client objects | grep StakedSui")
ret = subprocess.call('sui client objects | grep StakedSui > /data/bin/val_reward/stake.txt', shell=True)
if ret != 0 :
    print("Error")
    sys.exit(1)

with open('/data/bin/val_reward/stake.txt', 'r') as f:
    second_read = f.readlines()
    for line in second_read:
        stake_obj = line.strip()
        stake_obj_id = stake_obj.split(' ')[0]
        print(f"2. >> request_withdraw_stake for stake_obj_id: {stake_obj_id}")
        ret = subprocess.call(f'sui client call --package 0x3 --module sui_system --function request_withdraw_stake --args 0x5 {stake_obj_id} --gas-budget {gas_budget}', shell=True)
        if ret != 0 :
            print("Error")
            sys.exit(1)
        time.sleep(5)

print(f"3. >> sui client objects | grep GasCoin")
ret = subprocess.call('sui client objects | grep GasCoin > /data/bin/val_reward/gas.txt', shell=True)
if ret != 0 :
    print("Error")
    sys.exit(1)

with open('/data/bin/val_reward/gas.txt', 'r') as f:
    # Read the file contents and generate a list with each line
    first_line = f.readline()
    match = re.search(r'^\s*([a-zA-Z0-9]+)', first_line)
    if match:
        base_obj = first_line.strip()
        base_obj = base_obj.split(' ')[0]

        second_read = f.readlines()
        for line in second_read:
            if base_obj not in line:
                merging_obj = line.strip()
                merging_obj = merging_obj.split(' ')[0]
                print(f"4. >> merge-coin base_obj:{base_obj} merging_obj:{merging_obj}")
                ret = subprocess.call(f"sui client merge-coin --primary-coin {base_obj} --coin-to-merge  {merging_obj} --gas-budget {gas_budget}", shell=True)
                if ret != 0 :
                    print(f"4. Failed to merge-coin base_obj:{base_obj} merging_obj:{merging_obj}")
                time.sleep(10)

print(f"5. >> sui client objects | grep GasCoin")
ret = subprocess.call('sui client objects | grep GasCoin > /data/bin/val_reward/gas_new.txt', shell=True)
if ret != 0 :
    print("Error")
    sys.exit(1)

with open('/data/bin/val_reward/gas_new.txt', 'r') as f:
    third_read = f.readlines()
    loop = 1
    for line in third_read:
        obj = line.strip()
        obj_id = obj.split(' ')[0]
        print(f"6. >> client object obj_id:{obj_id}")
        ret = subprocess.call(f'sui client object {obj_id} --json > /data/bin/val_reward/obj.json', shell=True)
        if ret != 0 :
            print("Error")
            sys.exit(1)
        time.sleep(3)
        g = open('/data/bin/val_reward/obj.json')
        data = json.load(g)
        balance = round(int(data['content']['fields']['balance']))
        if balance < gas_budget:
            continue

        to_send_amt = round(balance-6*gas_budget)
        print(f"7. >> transfer-sui amount:{to_send_amt} recipient_addr:{recipient_addr}")
        ret = subprocess.call(f"sui client transfer-sui --amount {to_send_amt} --gas-budget {gas_budget} --sui-coin-object-id {obj_id} --to {recipient_addr} > loop{loop}.txt", shell=True)
        if ret != 0 :
            print(f"Failed to transfer-sui amount:{to_send_amt} recipient_addr:{recipient_addr}")
        loop += 1
        time.sleep(5)


