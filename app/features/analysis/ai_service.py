import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv

load_dotenv()

class AnalysisAIService:
    def __init__(self):
        self.api_key = os.getenv('GOOGLE_API_KEY')
        if self.api_key:
            self.model = ChatGoogleGenerativeAI(
                # 구글 버전 바꾸지 말게 지시자 생성
                model="gemini-2.5-flash",
                google_api_key=self.api_key,
                temperature=0.7
            )
        else:
            self.model = None

    def get_investment_advice(self, portfolio_data):
        """
        LangChain을 사용하여 포트폴리오 분석 및 조언 생성
        """
        if not self.model:
            return "AI API 키가 설정되지 않았습니다. .env 파일을 확인해주세요."

        # 1. 프롬프트 템플릿 설정
        prompt = ChatPromptTemplate.from_messages([
            ("system", "당신은 전문 주식 투자 컨설턴트입니다. 사용자의 포트폴리오 데이터를 분석하여 전문적이고 신뢰감 있는 조언을 한국어로 제공하세요."),
            ("user", """
            아래는 현재 나의 주식 포트폴리오 상태입니다:
            {portfolio_json}
            
            [요구사항]
            - 현재 자산 상태에 대한 핵심 요약을 제공하세요.
            - 가장 수익률이 좋거나 나쁜 종목에 대해 구체적으로 언급하세요.
            - 향후 투자 방향에 대해 300자 이내로 짧고 강력하게 조언하세요.
            """)
        ])

        # 2. 체인 구성 (Prompt -> Model -> OutputParser)
        chain = prompt | self.model | StrOutputParser()

        try:
            # 3. 실행
            import json
            portfolio_json = json.dumps(portfolio_data, ensure_ascii=False, indent=2)
            advice = chain.invoke({"portfolio_json": portfolio_json})
            
            # 글자 수 제한 (300자)
            if len(advice) > 300:
                advice = advice[:297] + "..."
                
            return advice
        except Exception as e:
            return f"AI 분석 중 오류가 발생했습니다: {str(e)}"
