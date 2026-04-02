# ArkGrid 젬 최적화 도구

![screenshot](screenshot.png)

LostArk의 스펙업 시스템인 **아크 그리드**에서 젬을 코어에 효율적으로 배치하기 위한 최적화 도구입니다.  
젬 목록을 입력하면 세 개의 코어에 가장 효율적인 배치를 자동으로 계산합니다.

## 주요 기능

- CSV 파일을 통한 젬 목록 불러오기
- 스프레드시트 붙여넣기 지원
- 젬 클릭으로 코어에 배치
- 자동 최적화 기능
- 코어 상태 시각화

## 기술 스택

| 구분 | 기술 |
|------|------|
| 프론트엔드 | HTML, CSS, JavaScript |
| 백엔드 | Python, FastAPI |
| API 문서 | Swagger UI (자동 생성) |

## 실행 방법

### 백엔드 서버 실행

```bash
pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

| 주소 | 내용 |
|------|------|
| http://127.0.0.1:8000 | 프론트엔드 |
| http://127.0.0.1:8000/docs | Swagger UI (API 테스트) |
| http://127.0.0.1:8000/redoc | ReDoc (API 문서) |

## API 엔드포인트

### 젬 관리 `/api/gems`

| 메서드 | 경로 | 설명 |
|--------|------|------|
| GET | `/api/gems` | 전체 젬 목록 조회 |
| POST | `/api/gems` | 젬 추가 |
| POST | `/api/gems/bulk` | 텍스트/CSV 일괄 추가 |
| DELETE | `/api/gems/{id}` | 젬 삭제 |
| DELETE | `/api/gems` | 전체 초기화 |

### 코어 관리 `/api/cores`

| 메서드 | 경로 | 설명 |
|--------|------|------|
| GET | `/api/cores` | 코어 3개 현황 조회 |
| GET | `/api/cores/{id}` | 특정 코어 조회 |
| PATCH | `/api/cores/{id}/grade` | 등급 변경 |
| POST | `/api/cores/{id}/assign` | 슬롯에 젬 배치 |
| DELETE | `/api/cores/{id}/slots/{index}` | 슬롯에서 젬 제거 |

### 최적화 `/api/optimize`

| 메서드 | 경로 | 설명 |
|--------|------|------|
| POST | `/api/optimize` | 최적 배치 계산 후 코어에 적용 |
| GET | `/api/optimize/preview` | 미리보기만 (적용 없음) |

## 프로젝트 구조

```
├── app/
│   ├── main.py          # FastAPI 앱 진입점
│   ├── store.py         # 인메모리 상태 저장소
│   ├── schemas.py       # Pydantic 요청/응답 스키마
│   ├── serializers.py   # 모델 → JSON 변환
│   ├── models/
│   │   ├── gem.py       # Gem 데이터 클래스
│   │   └── core.py      # Core 데이터 클래스 + 등급 정의
│   └── routers/
│       ├── gems.py      # 젬 관리 라우터
│       ├── cores.py     # 코어 관리 라우터
│       └── optimize.py  # 최적화 라우터 + 알고리즘
├── static/
│   └── index.html       # 프론트엔드
├── legacy/
│   └── index.html       # 기존 단일 HTML 버전
└── requirements.txt
```

## 목적

ArkGrid 젬 배치를 직접 계산하는 과정이 번거로워 편하게 최적 조합을 찾을 수 있도록 만든 도구입니다.  
이후 FastAPI를 활용한 RESTful API 백엔드로 리팩토링하여 포트폴리오 프로젝트로 발전시켰습니다.
