# Azure Application Gateway TLS Certificate Checker

Azure Application Gateway의 HTTPS 리스너에 연결된 TLS 인증서 정보를 자동으로 수집하고 CSV 파일로 저장하는 도구입니다.

## 기능

- Azure Application Gateway의 HTTPS 리스너 자동 탐지
- 각 도메인의 TLS 인증서 정보 수집
  - 도메인, 포트
  - 인증서 주체, 발급자
  - 유효기간 (시작일, 만료일)
  - 시리얼 번호, 버전
  - 인증서 상태
- 결과를 CSV 파일로 저장

## 사전 요구사항

- Python 3.7+
- Azure CLI 설치 및 로그인
- Azure 구독에 대한 적절한 권한

## 설치

1. 저장소 클론
```bash
git clone <repository-url>
cd cert-renew-check
```

2. 의존성 설치
```bash
pip install -r requirements.txt
```

## 설정

`settings/` 디렉토리에 있는 설정 파일을 수정하여 Azure 리소스 정보를 입력하세요:

```json
{
    "tenantId": "your-tenant-id",
    "subscriptionId": "your-subscription-id",
    "appgwName": "your-app-gateway-name",
    "appgwRgName": "your-resource-group-name",
    "resultFileName": "./results/your-result-file.csv"
}
```

## 사용법

```bash
python check-appgw-cert-info.py
```

실행하면:
1. Azure에 로그인하고 구독을 지정
2. Application Gateway의 HTTPS 리스너를 탐지
3. 각 도메인의 TLS 인증서 정보를 수집
4. 결과를 CSV 파일로 저장

## 결과 파일

결과는 `results/` 디렉토리에 CSV 파일로 저장되며, 다음 정보를 포함합니다:
- Domain, Port
- Subject, Issuer
- ValidFrom, ValidTo
- SerialNumber, Version
- Status

## 프로젝트 구조

```
cert-renew-check/
├── check-appgw-cert-info.py    # 메인 스크립트
├── requirements.txt            # Python 의존성
├── settings/                   # 설정 파일들
│   └── <your-settings>.settings.json
└── results/                    # 결과 CSV 파일들
    └── output.csv
```
