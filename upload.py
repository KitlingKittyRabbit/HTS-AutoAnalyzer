#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import paramiko
import random
import json
import requests
import time

with open('setting_data.json', 'r') as a:
    setting_data = json.load(a)
ssh_server_ip = setting_data['ssh_server_ip']
ssh_port = setting_data['ssh_port']
username = setting_data['username']
password = setting_data['password']
source_file_list = setting_data['source_file_list']
target_path = setting_data['target_path']

file_name = str(random.randint(10000000, 99999999))
setting_data['file_name'] = file_name

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(ssh_server_ip, ssh_port, username, password)
stdin, stdout, stderr = ssh.exec_command(f'mkdir {target_path}/{file_name}')
a = f'{target_path}/{file_name}'
if stdout.channel.recv_exit_status() != 0:
    print(stderr.read().decode())


def upload_file(server_ip: str, port: int, username: str, password: str, source_file: str, target_path: str, max_retries: int = 5, retry_delay: int = 30) -> None:
    '''
    通过SSH上传文件到服务器指定位置，并具有重试机制。

    参数:
        server_ip: 服务器地址
        port: 端口
        username: 用户名
        password: 密码
        source_file: 待上传的文件路径
        target_path: 服务器目标文件夹路径
        max_retries: 最大重试次数（默认5次）
        retry_delay: 每次重试之间的延迟时间（秒，默认30秒）
    '''
    retry_count = 0
    while retry_count < max_retries:
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(server_ip, port, username, password)

            sftp = ssh.open_sftp()
            print(f'{source_file}上传中')
            sftp.put(source_file, target_path)
            sftp.close()

            ssh.close()
            print(f'{source_file}上传成功')
            break
        except Exception as e:
            print(f"{source_file}上传失败:{e}")
            retry_count += 1
            if retry_count < max_retries:
                print(f"将在 {retry_delay} 秒后重试...")
                time.sleep(retry_delay)
            else:
                print("已达到最大重试次数，上传失败。")
                break


for source_file in source_file_list:
    upload_file(ssh_server_ip, ssh_port, username, password, source_file, f'{target_path}/{file_name}/{source_file}')
api_server_ip = setting_data['api_serve_ip']
api_port = setting_data['api_port']

url = f'{api_server_ip}/rna_seq_analysis'

response = requests.post(url, json=setting_data)

if response.status_code == 200:
    result = response.json()
    print(result)
else:
    print(response.text)
