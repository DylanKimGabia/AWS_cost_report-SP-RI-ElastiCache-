

AWS_ACCESS = "개인 키 발급 필요"
AWS_SECRET = "개인 키 발급 필요"

import boto3
import pandas as pd
import numpy as np
import json
import re
import warnings
from openpyxl.styles import Font

# 출력 설정
pd.set_option('display.max_columns', None)
pd.set_option('display.float_format', '{:.2f}'.format)
warnings.filterwarnings('ignore', category=FutureWarning)

class AWSUnifiedMasterEngine:
    def __init__(self, access_key, secret_key):
        self.client = boto3.client('pricing', aws_access_key_id=access_key, aws_secret_access_key=secret_key, region_name='us-east-1')
        self.monthly_hours = 730
        self.hours_1y, self.hours_3y = 8760, 26280
        self.loc_map = {'ap-northeast-2': 'Asia Pacific (Seoul)', 'us-east-1': 'US East (N. Virginia)'}
        
        # 옵션 정의
        self.ec2_tables = ["Compute Savings Plans", "EC2 Instance Savings Plans", "Standard Reserved Instance", "Convertible Reserved Instance"]
        self.ec2_config = {"Compute Savings Plans": "convertible", "EC2 Instance Savings Plans": "standard", "Standard Reserved Instance": "standard", "Convertible Reserved Instance": "convertible"}
        self.ec2_opts = [('No upfront, 1yr', 'no1y', 'No Upfront', '1'), ('No upfront, 3yr', 'no3y', 'No Upfront', '3'), ('All upfront, 1yr', 'all1y', 'All Upfront', '1'), ('All upfront, 3yr', 'all3y', 'All Upfront', '3')]
        self.rds_opts = [('Reserved Instance (No upfront, 1yr)', 'No Upfront', '1'), ('Reserved Instance (All upfront, 1yr)', 'All Upfront', '1'), ('Reserved Instance (All upfront, 3yr)', 'All Upfront', '3')]
        self.cache_opts = [('Reserved Node (No upfront, 1yr)', 'No Upfront', '1'), ('Reserved Node (No upfront, 3yr)', 'No Upfront', '3'), ('Reserved Node (All upfront, 1yr)', 'All Upfront', '1'), ('Reserved Node (All upfront, 3yr)', 'All Upfront', '3')]

    def fetch_ec2(self, region_code, itype, os_val, mode, lease='1', opt='No Upfront', off_class='standard'):
        if not self.client: return 0.0
        filters = [{'Type': 'TERM_MATCH', 'Field': 'regionCode', 'Value': region_code}, {'Type': 'TERM_MATCH', 'Field': 'instanceType', 'Value': itype}, {'Type': 'TERM_MATCH', 'Field': 'operatingSystem', 'Value': os_val}, {'Type': 'TERM_MATCH', 'Field': 'preInstalledSw', 'Value': 'NA'}, {'Type': 'TERM_MATCH', 'Field': 'tenancy', 'Value': 'Shared'}, {'Type': 'TERM_MATCH', 'Field': 'capacitystatus', 'Value': 'Used'}]
        try:
            resp = self.client.get_products(ServiceCode='AmazonEC2', Filters=filters, MaxResults=100)
            for j in resp.get('PriceList', []):
                data = json.loads(j)
                terms = data.get('terms', {})
                if mode == 'od' and 'OnDemand' in terms:
                    for _, o in terms['OnDemand'].items():
                        for _, d in o['priceDimensions'].items(): return float(d['pricePerUnit']['USD'])
                elif mode == 'ri' and 'Reserved' in terms:
                    for _, o in terms['Reserved'].items():
                        rattr = o.get('termAttributes', {})
                        if rattr.get('OfferingClass', '').lower() != off_class: continue
                        if re.sub(r'[^0-9]', '', str(rattr.get('LeaseContractLength', ''))) == lease and (opt in rattr.get('PurchaseOption', '')):
                            for _, d in o['priceDimensions'].items():
                                p = float(d['pricePerUnit']['USD'])
                                if p > 0: return p
            return 0.0
        except: return 0.0

    def fetch_rds(self, region_code, itype, engine, mode, lease='1', opt='No Upfront'):
        if not self.client: return 0.0
        loc = self.loc_map.get(region_code, 'Asia Pacific (Seoul)')
        filters = [{'Type': 'TERM_MATCH', 'Field': 'location', 'Value': loc}, {'Type': 'TERM_MATCH', 'Field': 'instanceType', 'Value': itype}, {'Type': 'TERM_MATCH', 'Field': 'databaseEngine', 'Value': engine}, {'Type': 'TERM_MATCH', 'Field': 'deploymentOption', 'Value': 'Single-AZ'}]
        try:
            resp = self.client.get_products(ServiceCode='AmazonRDS', Filters=filters, MaxResults=100)
            for j in resp.get('PriceList', []):
                data = json.loads(j)
                attr = data['product']['attributes']
                if 'IOOptimized' in attr.get('usagetype', ''): continue
                terms = data.get('terms', {})
                if mode == 'od' and 'OnDemand' in terms:
                    for _, o in terms['OnDemand'].items():
                        for _, d in o['priceDimensions'].items(): return float(d['pricePerUnit']['USD'])
                elif mode == 'ri' and 'Reserved' in terms:
                    for _, o in terms['Reserved'].items():
                        rattr = o.get('termAttributes', {})
                        if re.sub(r'[^0-9]', '', str(rattr.get('LeaseContractLength', ''))) == lease and (opt in rattr.get('PurchaseOption', '')):
                            for _, d in o['priceDimensions'].items():
                                p = float(d['pricePerUnit']['USD'])
                                if p > 0: return p
            return 0.0
        except: return 0.0

    def fetch_cache(self, region_code, itype, engine, mode, lease='1', opt='No Upfront'):
        if not self.client: return 0.0
        loc = self.loc_map.get(region_code, 'Asia Pacific (Seoul)')
        filters = [{'Type': 'TERM_MATCH', 'Field': 'location', 'Value': loc}, {'Type': 'TERM_MATCH', 'Field': 'instanceType', 'Value': itype}, {'Type': 'TERM_MATCH', 'Field': 'cacheEngine', 'Value': engine}]
        try:
            resp = self.client.get_products(ServiceCode='AmazonElastiCache', Filters=filters, MaxResults=100)
            for j in resp.get('PriceList', []):
                data = json.loads(j)
                terms = data.get('terms', {})
                if mode == 'od' and 'OnDemand' in terms:
                    for _, o in terms['OnDemand'].items():
                        for _, d in o['priceDimensions'].items(): return float(d['pricePerUnit']['USD'])
                elif mode == 'ri' and 'Reserved' in terms:
                    for _, o in terms['Reserved'].items():
                        rattr = o.get('termAttributes', {})
                        if re.sub(r'[^0-9]', '', str(rattr.get('LeaseContractLength', ''))) == lease and (opt in rattr.get('PurchaseOption', '')):
                            for _, d in o['priceDimensions'].items():
                                p = float(d['pricePerUnit']['USD'])
                                if p > 0: return p
            return 0.0
        except: return 0.0

    def _add_summary(self, df, opts, mode):
        # 1. Total 계산
        cols_to_sum = ['수량', '1년 요금', '3년 요금', '약정', '약정 단가']
        
        total = ['Total'] + [np.nan]*(len(df.columns)-1)
        for i, col in enumerate(df.columns):
            if col[1] in cols_to_sum:
                total[i] = df[col].apply(lambda x: 0 if x == "-" or pd.isna(x) else x).astype(float).sum()
        df.loc[len(df)] = total
        
        od_1y = df.iloc[-1][('On-Demand', '1년 요금')]
        od_3y = df.iloc[-1][('On-Demand', '3년 요금')]
        save_row, pct_row = ['On-Demand 대비'] + [np.nan]*(len(df.columns)-1), [np.nan]*len(df.columns)
        
        idx = 6
        for opt_tuple in opts:
            step = 4 if mode == 'RDS' else 6 
            
            # 1년 절감 계산
            col_1y_idx = idx + (2 if mode == 'RDS' else 4)
            c_total_1y = df.iloc[-1][(df.columns[idx][0], '1년 요금')]
            save_1y = od_1y - c_total_1y
            save_row[col_1y_idx] = save_1y
            if od_1y > 0: pct_row[col_1y_idx] = f"{(save_1y / od_1y) * 100:.2f}%"
            
            # 3년 절감 계산
            col_3y_idx = idx + (3 if mode == 'RDS' else 5)
            c_total_3y = df.iloc[-1][(df.columns[idx][0], '3년 요금')]
            save_3y = od_3y - c_total_3y
            save_row[col_3y_idx] = save_3y
            if od_3y > 0: pct_row[col_3y_idx] = f"{(save_3y / od_3y) * 100:.2f}%"

            idx += step
            
        df.loc[len(df)], df.loc[len(df)] = save_row, pct_row

        # [수정 1] 소수점 처리 로직 변경
        # '약정'만 3자리, '약정 단가' 등 나머지는 2자리
        for col in df.columns:
            if col[1] == '약정':  # 오직 '약정' 컬럼만
                df[col] = df[col].apply(lambda x: round(x, 3) if isinstance(x, (int, float)) and not pd.isna(x) else x)
            else:  # 나머지는 2자리
                df[col] = df[col].apply(lambda x: round(x, 2) if isinstance(x, (int, float)) and not pd.isna(x) else x)

        return df

    def calc_ec2(self, instances, region, os):
        res = {}
        cols = [('On-Demand', c) for c in ['인스턴스','수량','단가','월 요금','1년 요금','3년 요금']]
        for n, _, _, _ in self.ec2_opts: cols += [(n, c) for c in ['단가','약정 단가','약정','월 요금','1년 요금','3년 요금']]
        
        for tname in self.ec2_tables:
            rows = []
            target = self.ec2_config[tname]
            for itype, qty in instances.items():
                od_h = self.fetch_ec2(region, itype, os, 'od')
                od_m = od_h * self.monthly_hours * qty
                
                # EC2 On-Demand 단가: 월간 단가로 변경
                od_unit_monthly = od_h * self.monthly_hours
                row = [itype, qty, od_unit_monthly, od_m, od_m*12, od_m*36]
                
                for _, _, opt, yr in self.ec2_opts:
                    p = self.fetch_ec2(region, itype, os, 'ri', yr, opt, target)
                    if opt == 'No Upfront':
                        u = p * self.monthly_hours
                        row += [u, p, p*qty, u*qty, u*qty*12, u*qty*36]
                    else:
                        months = 12 if yr == '1' else 36
                        monthly_amortized = (p * qty) / months
                        ch = p / (self.hours_1y if yr=='1' else self.hours_3y)
                        row += [p, ch, ch*qty, monthly_amortized, p*qty if yr=='1' else (p*qty)/3, p*qty if yr=='3' else (p*qty)*3]
                rows.append(row)
            res[tname] = self._add_summary(pd.DataFrame(rows, columns=pd.MultiIndex.from_tuples(cols)), self.ec2_opts, 'EC2')
        return res

    def calc_rds(self, instances, region):
        cols = [('On-Demand', c) for c in ['인스턴스','수량','단가','월 요금','1년 요금','3년 요금']]
        for n, _, yr in self.rds_opts: cols += [(n, c) for c in ['단가','월 요금','1년 요금','3년 요금']]
        
        rows = []
        for k, qty in instances.items():
            itype, eng = k.split('::')
            od_h = self.fetch_rds(region, itype, eng, 'od')
            od_m = od_h * self.monthly_hours * qty
            row = [f"{itype}_{eng}", qty, od_h*self.monthly_hours, od_m, od_m*12, od_m*36]
            for _, opt, yr in self.rds_opts:
                p = self.fetch_rds(region, itype, eng, 'ri', yr, opt)
                if opt == 'No Upfront':
                    u = p * self.monthly_hours
                    cost_1y = u * qty * 12
                    cost_3y = u * qty * 36
                    row += [u, u*qty, cost_1y, cost_3y]
                else:
                    months = 12 if yr == '1' else 36
                    monthly_amortized = (p * qty) / months
                    cost_1y = p * qty if yr == '1' else (p * qty) / 3
                    cost_3y = (p * qty) * 3 if yr == '1' else p * qty
                    row += [p, monthly_amortized, cost_1y, cost_3y]
            rows.append(row)
        return {"Reserved Instance": self._add_summary(pd.DataFrame(rows, columns=pd.MultiIndex.from_tuples(cols)), self.rds_opts, 'RDS')}

    def calc_cache(self, instances, region):
        cols = [('On-Demand', c) for c in ['인스턴스','수량','단가','월 요금','1년 요금','3년 요금']]
        for n, _, _ in self.cache_opts: cols += [(n, c) for c in ['단가','약정 단가','약정','월 요금','1년 요금','3년 요금']]
        rows = []
        for k, qty in instances.items():
            itype, engine = k.split('::')
            od_h = self.fetch_cache(region, itype, engine, 'od')
            od_m = od_h * self.monthly_hours * qty
            row = [f"{itype} ({engine})", qty, od_h*self.monthly_hours, od_m, od_m*12, od_m*36]
            for _, opt, yr in self.cache_opts:
                p = self.fetch_cache(region, itype, engine, 'ri', yr, opt)
                if opt == 'No Upfront':
                    u = p * self.monthly_hours
                    row += [u, p, p*qty, u*qty, u*qty*12, u*qty*36]
                else:
                    months = 12 if yr == '1' else 36
                    monthly_amortized = (p * qty) / months
                    ch = p / (self.hours_1y if yr=='1' else self.hours_3y)
                    row += [p, ch, ch*qty, monthly_amortized, p*qty if yr=='1' else (p*qty)/3, p*qty if yr=='3' else (p*qty)*3]
            rows.append(row)
        return {"Reserved Node": self._add_summary(pd.DataFrame(rows, columns=pd.MultiIndex.from_tuples(cols)), self.cache_opts, 'Cache')}

if __name__ == "__main__":
    eng = AWSUnifiedMasterEngine(AWS_ACCESS, AWS_SECRET)
    final = {}
    print("=== AWS 정밀 산출 시스템 (v3.5 Final Fixed) ===")
    reg = input("리전 (기본: ap-northeast-2): ") or "ap-northeast-2"
    
    # 1. EC2
    ec2_in, os_v = {}, input("EC2 OS (기본: Linux): ") or "Linux"
    while True:
        t = input("EC2 타입 (q 종료): ")
        if t.lower() == 'q': break
        try: ec2_in[t] = int(input(f" {t} 수량: "))
        except: pass
    if ec2_in: final['EC2'] = eng.calc_ec2(ec2_in, reg, os_v)

    # 2. RDS
    rds_in = {}
    while True:
        t = input("RDS 타입 (q 종료): ")
        if t.lower() == 'q': break
        e = input(f" {t} 엔진: ")
        try: rds_in[f"{t}::{e}"] = int(input(f" {t} 수량: "))
        except: pass
    if rds_in: final['RDS'] = eng.calc_rds(rds_in, reg)

    # 3. Cache
    cache_in = {}
    print("\n[ElastiCache 엔진: Redis, Memcached, Valkey 중 선택]")
    while True:
        t = input("Cache 타입 (q 종료): ")
        if t.lower() == 'q': break
        e = input(f" {t} 엔진 (기본: Redis): ") or "Redis"
        try: cache_in[f"{t}::{e}"] = int(input(f" {t} 수량: "))
        except: pass
    if cache_in: final['ElastiCache'] = eng.calc_cache(cache_in, reg)

    # 저장
    if final:
        with pd.ExcelWriter("AWS_Report_Final_V3_5.xlsx", engine='openpyxl') as writer:
            for sheet, tables in final.items():
                curr = 0
                for tname, df in tables.items():
                    df.to_excel(writer, sheet_name=sheet, startrow=curr+1)
                    writer.sheets[sheet].cell(row=curr+1, column=1, value=f"■ {tname}").font = Font(bold=True)
                    curr += len(df) + 6
        print("\n Done ! ")
