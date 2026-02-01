# AWS 예산 추정 자동화

### 제작자 :
**클라우드사업팀 인턴 Dylan(김동현)**

### 목적 : 고객사 환경에 맞는 최적의 비용 절감안 도출
  -  AWS 인프라(EC2, RDS, ElastiCache)의 On-Demand 및 약정(Savings Plans, RI)


![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python&logoColor=white)
![AWS](https://img.shields.io/badge/AWS-Pricing%20API-orange?logo=amazon-aws&logoColor=white)

 

 

---

## 1. Work Stream
1. **Auth:** AWS Pricing API (us-east-1) 연동
2. **Config:** 리전(Region) / OS / 테넌시 등 환경 변수 설정
3. **Input:** 서비스별 인스턴스 타입 / 엔진 / 수량 입력 (Loop)
4. **Logic:** 서비스별 전용 필터링 및 교차 비용 추산
5. **Output:** `AWS_예산안.xlsx` 자동 생성

---

## 2. Calculation Logic
모든 비용은 **USD($)** 기준이며, AWS 공식 월평균 시간(`730시간`)을 적용

### [공통 기준] (Time Basis)
| 기준 (Basis) | 시간 (Hours) | 비고 |
| :--- | :---: | :--- |
| **Monthly** | `730` | AWS 공식 월평균 시간 |
| **1 Year** | `8,760` | 730 × 12 |
| **3 Years** | `26,280` | 730 × 36 |

### 2_1. Amazon EC2
- **대상:** Compute SP, Instance SP, Standard RI, Convertible RI
- **필터:** Shared Tenancy, Used Capacity, Standard Offering Class

| 유형 | 항목 | 산출 수식 (Formula) |
| :--- | :--- | :--- |
| **On-Demand** | 1년 비용 | $Hourly_{OD} \times 8,760 \times Qty$ |
| **No Upfront** | 1년 비용 | $Hourly_{RI} \times 8,760 \times Qty$ |
| **All Upfront** | 월 환산액 | $\frac{Upfront_{Fee} \times Qty}{Months(12\ or\ 36)}$ |
| | 1년 비용 | $Upfront_{Fee} \times Qty$ (1년 약정 시) |

### 2_2. Amazon RDS
- **대상:** Aurora, Oracle, PostgreSQL, MySQL, MariaDB 등
- **필터:** Single-AZ, Standard Edition (IOOptimized 제외)
- **로직:** 1년 약정 데이터로 3년치 추산 / 3년 약정 데이터로 1년치 역산

| 유형 | 항목 | 산출 수식 (Formula) |
| :--- | :--- | :--- |
| **On-Demand** | 1년 비용 | $Monthly_{OD} \times 12 \times Qty$ |
| **No Upfront** | 1년 비용 | $Hourly_{RI} \times 8,760 \times Qty$ |
| **All Upfront** | 1년 추산 | $(Upfront_{3yr} \times Qty) \div 3$ (3년 약정 데이터 역산) |
| | 3년 추산 | $(Upfront_{1yr} \times Qty) \times 3$ (1년 약정 데이터 추산) |

### 2_3. Amazon ElastiCache
- **대상:** Redis, Memcached, Valkey
- **단가:** 노드(Node) 기준

| 유형 | 항목 | 산출 수식 (Formula) |
| :--- | :--- | :--- |
| **On-Demand** | 1년 비용 | $Hourly_{OD} \times 8,760 \times Qty$ |
| **All Upfront** | 월 환산액 | $\frac{Upfront_{Fee} \times Qty}{Months}$ |

---

## Savings Rate (절감률)
On-Demand 대비 약정 옵션 선택 시 절감되는 비율을 백분율로 표기됩니다.

$$
\text{Savings Rate (\%)} = \left( \frac{\text{On-Demand Cost} - \text{Commitment Cost}}{\text{On-Demand Cost}} \right) \times 100
$$

---

## Disclaimer
1. **API 실시간성:** 실행 시점의 AWS Price List API 데이터를 기준으로 합니다.
2. **데이터 전처리:** EC2는 Pre-installed S/W가 없는 `NA` 기준입니다.
3. **정밀도:** 엑셀 표기는 소수점 둘째 자리 반올림이나, 내부 연산은 `float` 정밀도를 유지합니다.

---
Copyright © 2026 Dylan (Donghyun Kim). All rights reserved.
