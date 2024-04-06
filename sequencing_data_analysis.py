# -*- coding: utf-8 -*-
import pandas as pd
import subprocess
import DEGA
import multiprocessing
from typing import Literal


class SequencingDataAnalysis():
    '''
    所有测序分析类的父类
    '''
    path = str

    def __init__(self, sample_name_list: list[str], grouping_list: list[str],
                 chr_and_length_path: path | None = None, gtf_path: path | None = None,
                 sequencing_type: Literal[1, 2] = 2, output_path: path = '', genome_path: path | None = None,
                 fastq_path_list: list[list[path]] | list[path] | None = None) -> None:
        '''
        参数：
            sample_name_list:样本名称列表，类似['c1','c2','e1','e2']
            grouping_list:分组信息列表，类似于['con','con','exp','exp']
            chr_and_length_path：染色体-长度表格路径，表格为csv文件，两列，一列名称，一列长度，无列名,默认为None
            gtf_path:gtf注释文件的路径，注释文件中需删除前几列带#的注释行,默认为None
            sequencing_type:测序类型,1为单端测序,2为双端测序,默认为2
            output_path:输出文件夹路径,默认为一个空字符串
            genome_path:参考基因组.fasta格式文件路径
            fastq_path_list:fastq文件路径列表,若为单端测序,类似[1.fastq,2.fastq],若为双端测序,类似[[1_r1.fastq,1_r2.fastq],[2_r1.fastq,2_r2.fastq]],默认为None

        属性：
            sample_name_list:样本名称列表
            grouping_list:分组信息列表
            chr_length_dic:储存有{染色体名:染色体长度}的字典
            gtf_path:gtf注释文件路径
            gtf_df:gtf注释文件的dataframe
            sequencing_type:测序类型,1为单端测序,2为双端测序,默认为2
            output_path:输出文件夹路径,默认为一个空字符串
            genome_path:参考基因组.fasta格式文件路径
            fastq_cleaned_path_list:被fastp预处理后的fastq文件路径列表

        输出文件：
            *.fq:原始fastq数据被fastp软件预处理后的结果
        '''
        if fastq_path_list is not None:
            fastq_cleaned_path_list = []
            if sequencing_type == 1:
                for i, fastq_path in enumerate(fastq_path_list):
                    data_clean = subprocess.run([f'fastp -i {fastq_path} -o {output_path}/{sample_name_list[i]}.fq'],
                                                shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                    print(data_clean.stdout)
                    fastq_cleaned_path_list.append(f'{output_path}/{sample_name_list[i]}.fq')
                    if data_clean.stderr:
                        print(data_clean.stderr)
            elif sequencing_type == 2:
                for i, fastq_path in enumerate(fastq_path_list):
                    data_clean = subprocess.run([f'fastp -i {fastq_path[0]} -I {fastq_path[1]} -o {output_path}/{sample_name_list[i]}_r1.fq -O {output_path}/{sample_name_list[i]}_r2.fq'],
                                                shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                    print(data_clean.stdout)
                    fastq_cleaned_path_list.append([f'{output_path}/{sample_name_list[i]}_r1.fq', f'{output_path}/{sample_name_list[i]}_r2.fq'])
                    if data_clean.stderr:
                        print(data_clean.stderr)
            self.fastq_cleaned_path_list = fastq_cleaned_path_list

        if gtf_path is not None:
            gtf_df = pd.read_csv(gtf_path, header=None, sep='\t')
            gtf_df = gtf_df.dropna()
            self.gtf_df = gtf_df
            self.gtf_path = gtf_path

        if chr_and_length_path is not None:
            chr_length_dic = {}
            chr_length_df = pd.read_csv(chr_and_length_path)
            chr_list = list(chr_length_df.iloc[:, 0])
            length_list = list(chr_length_df.iloc[:, 1])
            for chri, lengthi in zip(chr_list, length_list):
                chr_length_dic[chri] = lengthi
            self.chr_length_dic = chr_length_dic

        self.sequencing_type = sequencing_type
        self.sample_name_list = sample_name_list
        self.grouping_list = grouping_list
        self.output_path = output_path
        self.genome_path = genome_path

    def sam2bam_by_samtools(self, cpu_num: int, sam_path_list: list[path]) -> list[path]:
        '''
        用samtools将.sam文件转化为.bam文件并排序

        参数:
            cpu_num:使用的线程数
            sam_path_list:sam文件路径列表

        返回:
            bam_path_list:生成的.bam文件的路径列表

        输出文件:
            sorted_*.bam:.sam文件转化并排序得到的.bam文件
        '''
        bam_path_list = []
        sample_name_list = self.sample_name_list
        for i, sam_path in enumerate(sam_path_list):
            sam2bam = subprocess.run([f'samtools view -@ {cpu_num} -bS {sam_path} | samtools sort -@ {cpu_num} -o {self.output_path}/{sample_name_list[i]}_sorted.bam'],
                                     shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            print(sam2bam.stdout)
            if sam2bam.stderr:
                print(sam2bam.stderr)
            bam_path_list.append(f'{self.output_path}/{sample_name_list[i]}_sorted.bam')
        return bam_path_list


class RnaSeqAnalysis(SequencingDataAnalysis):
    '''
    用于分析转录组数据的类
    '''
    path = str

    def creat_index_by_hisat2(self, reference_genome_path: path | None = None, index_prefix: str = 'index_prefix') -> None:
        '''
        用hisat2构建参考基因组索引

        参数:
            reference_genome_path:参考基因组.fasta文件路径
            index_prefix:参考基因组索引前缀

        输出文件:
            *.ht2:参考基因组索引文件
        '''
        if reference_genome_path is None:
            reference_genome_path = self.genome_path
        creat_index = subprocess.run([f'hisat2-build {reference_genome_path} {self.output_path}/{index_prefix}'],
                                     shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        print(creat_index.stdout)
        if creat_index.stderr:
            print(creat_index.stderr)

    def mapping_by_hisat2(self, cpu_num: int, index_prefix: str, fastq_cleaned_path_list: list[path] | None = None) -> list[path]:
        '''
        用hisat2将预处理后的.fastq文件比对到参考基因组

        参数:
            cpu_num:比对所使用的线程数
            index_prefix:参考基因组索引前缀
            fastq_cleaned_data_path:预处理后的.fastq文件路径列表,若实例化时提供了原始数据路径则不需要指定

        返回:
            sam_path_list:生成的.sam文件的路径列表

        输出文件:
            *.sam:比对后得到的.sam文件
        '''
        if fastq_cleaned_path_list is None:
            fastq_cleaned_path_list = self.fastq_cleaned_path_list
        sam_path_list = []
        if self.sequencing_type == 1:
            for i, fastq_cleaned_path in enumerate(fastq_cleaned_path_list):
                mapping = subprocess.run([f'hisat2 -p {cpu_num} -x {index_prefix} -U {fastq_cleaned_path} -S {self.output_path}/{self.sample_name_list[i]}.sam'],
                                         shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                print(mapping.stdout)
                if mapping.stderr:
                    print(mapping.stderr)
                sam_path_list.append(f'{self.output_path}/{self.sample_name_list[i]}.sam')
        elif self.sequencing_type == 2:
            for i, fastq_cleaned_path in enumerate(fastq_cleaned_path_list):
                mapping = subprocess.run([f'hisat2 -p {cpu_num} -x {index_prefix} -1 {fastq_cleaned_path[0]} -2 {fastq_cleaned_path[1]} -S {self.output_path}/{self.sample_name_list[i]}.sam'],
                                         shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                print(mapping.stdout)
                if mapping.stderr:
                    print(mapping.stderr)
                sam_path_list.append(f'{self.output_path}/{self.sample_name_list[i]}.sam')
        return sam_path_list

    def count_by_HTSeq(self, bam_path_list: list[path], gtf_path: path | None = None) -> None:
        '''
        用HTSeq计数比对到各基因外显子的read数

        参数:
            bam_path_list:.bam文件路径列表
            gtf_path:.gtf文件路径

        输出文件:
            count.csv:计数结果文件
        '''
        if gtf_path is None:
            gtf_path = self.gtf_path

        def bam_count(bam_path):
            mapping = subprocess.run([f'htseq-count -m union {bam_path} {gtf_path} > {self.output_path}/{self.sample_name_list[i]}_counts.txt'],
                                     shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            print(mapping.stdout)
            if mapping.stderr:
                print(mapping.stderr)

        count_path_list = []
        processes = []
        for i, bam_path in enumerate(bam_path_list):
            p = multiprocessing.Process(target=bam_count, args=(bam_path,))
            processes.append(p)
            p.start()
            count_path_list.append(f'{self.output_path}/{self.sample_name_list[i]}_counts.txt')
        for p in processes:
            p.join()

        count_dataframe_list = []
        for count_path, sample_name in zip(count_path_list, self.sample_name_list):
            count_dataframe = pd.read_csv(count_path, sep="\t", header=None)
            count_dataframe = count_dataframe.iloc[:-5]
            count_dataframe.columns = ['', f'{sample_name}']
            count_dataframe_list.append(count_dataframe)

        merge = count_dataframe_list[0]
        for i in range(len(count_dataframe_list) - 1):
            merge = pd.merge(merge, count_dataframe_list[i + 1])
        merge.to_csv(f"{self.output_path}/count.csv", index=False)

    def diff_express_analysis_by_DEGA(self, count_path: path | None = None, phenotype_path: path | None = None) -> None:
        '''
        用DEGA进行差异表达分析

        参数:
            count_path:计数文件路径,每行为一个基因,每列为一个样本,默认为f'{self.output_path}/count.csv'

        输出文件:
            DEGA.csv:差异表达分析的结果
        '''
        if count_path is None:
            count_path = f'{self.output_path}/count.csv'
        if phenotype_path is None:
            phenotype_df = pd.DataFrame({'group': self.grouping_list}, index=self.sample_name_list)
        else:
            phenotype_df = pd.read_csv(phenotype_path, index_col=0)
        count_df = pd.read_csv(count_path, index_col=0)
        count_df = count_df.dropna()
        count_df = count_df[phenotype_df.index]
        dega = DEGA.dataset(count_df, phenotype_df, designFormula='group')
        dega.analyse()
        result = dega._results()
        result = result.dropna(subset=['adjusted p-value (group)'])
        result.to_csv(f'{self.output_path}/DEGA.csv')
