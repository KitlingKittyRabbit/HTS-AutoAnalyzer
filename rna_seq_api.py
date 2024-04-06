#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flask import Flask, request, jsonify
from sequencing_data_analysis import RnaSeqAnalysis
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from typing import List

app = Flask(__name__)


def send_email_with_attachment(sender_email: str, sender_password: str, receiver_email: str,
                               subject: str, body: str, file_path_list: List[str]) -> None:
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    for file_path in file_path_list:
        attachment = open(file_path, 'rb')
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(attachment.read())
        encoders.encode_base64(part)
        attachment.close()
        part.add_header('Content-Disposition', f'attachment; filename= {os.path.basename(file_path)}')
        msg.attach(part)

    server = smtplib.SMTP_SSL('smtp.qq.com', 465)
    server.login(sender_email, sender_password)
    server.sendmail(sender_email, receiver_email, msg.as_string())
    server.quit()
    print("邮件已成功发送！")


@app.route('/rna_seq_analysis', methods=['POST'])
def rna_seq_analysis():
    try:
        data = request.json
        sample_name_list = data['sample_name_list']
        grouping_list = data['grouping_list']
        chr_and_length_path = f"{data['target_path']}/{data['file_name']}/{data['chr_and_length']}"
        gtf_path = f"{data['target_path']}/{data['file_name']}/{data['gtf']}"
        sequencing_type = data['sequencing_type']
        fastq_path_list = [(f"{data['target_path']}/{data['file_name']}/" + x) for x in data['fastq_list']]
        genome_path = f"{data['target_path']}/{data['file_name']}/{data['reference_genome']}"
        index_prefix = data['index_prefix']
        cpu_num = data['cpu_num']
        output_path = f"{data['target_path']}/{data['file_name']}"
        data_analysis = RnaSeqAnalysis(sample_name_list, grouping_list, chr_and_length_path=chr_and_length_path, gtf_path=gtf_path,
                                       sequencing_type=sequencing_type, output_path=output_path, genome_path=genome_path, fastq_path_list=fastq_path_list)
        data_analysis.creat_index_by_hisat2(index_prefix=index_prefix)
        sam_path_list = data_analysis.mapping_by_hisat2(cpu_num, f"{data['target_path']}/{data['file_name']}/{index_prefix}")
        bam_path_list = data_analysis.sam2bam_by_samtools(cpu_num, sam_path_list)
        data_analysis.count_by_HTSeq(bam_path_list)
        data_analysis.diff_express_analysis_by_DEGA()

        sender_email = data['sender_email']
        sender_password = data['sender_password']
        receiver_email = data['email_address']
        subject = '转录组学分析结果'
        body = '您的转录组学分析结果,请查收'
        file_path_list = [f'{output_path}/count.csv', f'{output_path}/DEGA.csv']
        send_email_with_attachment(sender_email, sender_password, receiver_email, subject, body, file_path_list)

        return jsonify('数据处理完成，请检查邮箱')
    except Exception as e:
        return jsonify(f'{e}')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
