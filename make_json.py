#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
setting_data = {}
setting_data['ssh_server_ip'] = 'balabala'
setting_data['ssh_port'] = 22
setting_data['username'] = 'balabala'
setting_data['password'] = 123456
setting_data['source_file_list'] = ['chr_length.csv', 'saline_12h_1.fastq', 'saline_12h_2.fastq', 'saline_12h_3.fastq',
                                    'lps_12h_1.fastq', 'lps_12h_2.fastq', 'lps_12h_3.fastq', 'genomic1.gtf',
                                    'GCF_016699485.2_bGalGal1.mat.broiler.GRCg7b_genomic.fna']
setting_data['target_path'] = 'balabala'
setting_data['api_serve_ip'] = 'balabala'
setting_data['api_port'] = 1234
setting_data['sample_name_list'] = ['s1', 's2', 's3', 'l1', 'l2', 'l3']
setting_data['grouping_list'] = ['saline_12h', 'saline_12h', 'saline_12h', 'lps_12h', 'lps_12h', 'lps_12h']
setting_data['chr_and_length'] = 'chr_length.csv'
setting_data['gtf'] = 'genomic1.gtf'
setting_data['sequencing_type'] = 1
setting_data['fastq_list'] = ['saline_12h_1.fastq', 'saline_12h_2.fastq', 'saline_12h_3.fastq',
                              'lps_12h_1.fastq', 'lps_12h_2.fastq', 'lps_12h_3.fastq']
setting_data['reference_genome'] = 'GCF_016699485.2_bGalGal1.mat.broiler.GRCg7b_genomic.fna'
setting_data['index_prefix'] = 'index_prefix'
setting_data['cpu_num'] = 30
setting_data['email_address'] = 'balabala'
setting_data['sender_email'] = 'balabala'
setting_data['sender_password'] = 'balabala'
with open('setting_data.json', 'w') as x:
    json.dump(setting_data, x)
