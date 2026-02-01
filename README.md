AWS 통합 정밀 산출 시스템 (AWS Unified Master Engine)
목적 : AWS 인프라(EC2, RDS, ElastiCache)의 On-Demand 및 약정(Savings Plans, RI) 예산 산출 자동화

제작자 : Gabia 클라우드사업팀 인턴 Dylan(김동현)

------------------------------------------------------------------------------------------------------------------------------------

1. Table별 산출 함수 정의

1_1. Amazon EC2 (Compute / Instance SP, RI)
<img width="607" height="451" alt="image" src="https://github.com/user-attachments/assets/180ae16c-93a8-4169-8261-416e30a55a09" />

1_2. Amazon RDS (Reserved Instance)
<img width="604" height="438" alt="image" src="https://github.com/user-attachments/assets/549d19e9-7362-4d1e-b7ba-ad0ef580e06d" />

1_3. Amazon ElastiCache (Reserved Node)
<img width="514" height="219" alt="image" src="https://github.com/user-attachments/assets/fe3dc860-1368-4f65-9e46-637c3acd09b9" />


2. 절감율 (Saving %) 산출 수식
<img width="495" height="196" alt="image" src="https://github.com/user-attachments/assets/1a1d65bd-357a-473a-91d0-1105bb25a1db" />

------------------------------------------------------------------------------------------------------------------------------------

3. 특이사항

3_1. API 실시간성 : 본 도구는 실행 시점의 AWS Price List API 데이터를 가져오므로 AWS의 가격 정책 변경 시 산출 결과가 달라질 수 있습니다.
3_2. 반올림: 최종 엑셀 파일은 소수점 둘째 자리까지 표기되나 내부 계산은 정밀한 실수형(float)으로 처리됩니다.


------------------------------------------------------------------------------------------------------------------------------------

