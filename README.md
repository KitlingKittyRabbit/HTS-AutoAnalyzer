# HTS-AutoAnalyzer
用于高通量测序数据的自动分析,当前只完成了转录组数据分析的部分功能
## 原理
运行upload.py会在服务器指定目录下创建一个由随机8位数命名的文件夹,并上传相关文件到该文件夹内,随后调用事先在服务器端部署的接口rna_seq_api.py,分析便会自动进行,最终结果(计数和差异表达分析)会以邮件的形式发送
## 使用方法
### 1.使用make_json.py制作配置文件
修改make_json.py文件中对setting_data字典各键的赋值,其中
- 'ssh_server_ip'为用于ssh连接的服务器ip
- 'ssh_port'为ssh连接的端口,通常为22
- 'username'和'password'为ssh连接的用户名和密码
- 'source_file_list'是要上传的所有文件所组成的列表
- 'target_path'是文件要上传到的目录
- 'api_serve_ip'和'api_port'为api所在服务器的ip和端口
- 'sample_name_list'为样本名
- 'grouping_list'为分组情况,与样本名对应
- 'chr_and_length'为染色体及其长度表,要求是csv文件,共两列,第一列是染色体名称,第二列为长度
- 'gtf'为参考基因组配套的gtf注释文件,需要删除文件前几行带#的注释行
- 'sequencing_type'为测序类型,其中1为单端测序,2为双端测序
- 'fastq_list'为fastq文件列表,顺序也要与sample_name对应
- 'reference_genome'为参考基因组的fasta文件
- 'index_prefix'为使用hisat2构建参考基因组索引时的前缀名,不重要,可以随便填
- 'cpu_num'为调用支持多线程的外部软件(如hisat2)时使用的线程数
- 'email_address'为你要用来接收结果的邮箱地址
- 'sender_email'和'sender_password'为你要用来发送结果的邮箱地址和密码
修改完成后,运行make_json.py,就可以得到json格式的配置文件
### 2.部署rna_seq_api.py
在服务器上安装fastp、hisat2、samtools、HTSeq以及所有sequencing_data_analysis.py与rna_seq_api.py开头import的库,将sequencing_data_analysis.py与rna_seq_api.py放在服务器同一个文件夹下,运行rna_seq_api.py
### 3.运行upload.py
在客户端电脑安装upload.py所引用的库，将upload.py、配置文件以及所有要上传的文件放在客户端电脑的同一个文件夹下,运行upload.py,耐心等待即可
