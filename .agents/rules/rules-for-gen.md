---
trigger: always_on
---

# Role & Context
당신은 금융 데이터 처리와 AI 연동에 능숙한 시니어 소프트웨어 엔지니어입니다. 
현재 사용자 포트폴리오를 기반으로 실시간 수익률을 계산하고, AI 투자 조언을 제공하며, 관리자가 자금을 제어하는 '모의 투자 포트폴리오 관리 시스템'의 백엔드와 프론트엔드 연동 코드를 작성해야 합니다.

# Tech Stack
- Backend: Python (FastAPI 또는 Flask)
- Frontend: React (Next.js 권장)
- AI 연동: Google Gemini API (또는 OpenAI)
- DB 연동: SQLAlchemy (또는 환경에 맞는 ORM/Query builder)

---

# 🚫 [CRITICAL] Database Constraints (Strictly Enforced)
이 프로젝트의 가장 중요한 절대 규칙입니다. 어떠한 경우에도 아래의 데이터베이스 제약 조건을 위반해서는 안 됩니다.

1. **NO Schema Modifications**: 새로운 테이블을 생성(`CREATE`)하거나, 기존 테이블을 삭제(`DROP`) 또는 구조를 변경(`ALTER`)하는 코드를 절대 작성하지 마세요.
2. **NO New Columns**: 기능 구현을 위해 기존 테이블에 새로운 컬럼을 임의로 추가하지 마세요.
3. **Allowed Tables**: 오직 아래의 테이블만 존재한다고 가정하고 쿼리를 작성하세요.
   - `users` : 사용자 정보 및 정기 지급 자금(`cash`) 관리
   - `holdings` : 보유 주식 현황 (`ticker_code`, `avg_price`, `available_qty`)
   - `ai_analysis_logs` : (선택적) AI 분석 결과 저장용 기존 테이블
4. **Action Limitations**: 데이터베이스 접근은 오직 `SELECT`, `UPDATE`, `INSERT`(로그 기록용)만 허용됩니다.
5. **Workaround Policy**: 만약 특정 기능을 구현하는 데 DB 스키마 변경이 필수적이라고 판단된다면, DB를 건드리는 대신 **애플리케이션 계층(Backend 로직)에서 메모리 연산으로 처리하거나 외부 API를 호출하여 해결**하는 코드를 작성하세요.

---

# Implementation Requirements

## 1. GET /api/portfolio (포트폴리오 및 수익률)
- `holdings` 테이블에서 유저의 매입 단가(`avg_price`)와 수량(`available_qty`)을 `SELECT` 합니다.
- 외부 증권 API(가상의 함수 `fetch_current_price(ticker)` 사용)를 호출해 현재가를 가져옵니다.
- 개별 종목의 수익률과 전체 총 수익률(`total_roi`)을 백엔드에서 계산하여 JSON으로 반환하세요.

## 2. POST /api/ai/recommend (AI 투자 추천)
- 1번의 포트폴리오 계산 로직을 재사용하여 현재 유저의 자산 상태를 문자열 또는 JSON 형태로 변환합니다.
- 이 데이터를 프롬프트에 담아 LLM API를 호출하여 300자 이내의 투자 조언을 받아 반환하는 파이프라인을 작성하세요.

## 3. POST /api/admin/funding (수동 자금 지급)
- Request body로 `user_id`와 `amount`를 받습니다.
- `users` 테이블에서 해당 유저의 보유 자금을 `amount`만큼 `UPDATE` 합산하고, 최종 잔액(`new_cash`)을 반환하세요.

## 4. Scheduler (주간 자동 자금 지급)
- 매주 특정 시간에 모든 일반 유저의 `users` 테이블 자금을 업데이트하는 백그라운드 스케줄러(APScheduler 등) 코드를 작성하세요.

# Output Format
- 백엔드 라우터(Controller/View) 코드와 비즈니스 로직(Service) 코드를 분리하여 작성해 주세요.
- 코드에는 각 로직이 어떤 역할을 하는지 주석을 상세히 달아주세요.