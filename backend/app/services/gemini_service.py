"""
Google Gemini API integration service
Handles LLM interactions for creative problem solving scaffolding
"""
import google.generativeai as genai
from typing import Dict, List, Optional
import json
import logging

from ..core.config import settings

logger = logging.getLogger(__name__)


class GeminiService:
    """Service for interacting with Google Gemini API"""

    def __init__(self):
        """Initialize Gemini API with configuration"""
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')

        # System prompt for CPS scaffolding
        self.system_prompt = """당신은 예비교사들의 창의적 문제해결(CPS)을 돕는 메타인지 촉진 에이전트입니다.

역할: 창의적 메타인지 촉진자
목표: 학습자가 CPS 과정에서 깊이 있게 사고하도록 1-2문장의 질문 제공

CPS 단계:
1. 도전 이해 (기회 구성, 자료 탐색, 문제 구조화)
   - 기회 구성: 문제 해결의 건설적 목표 식별
   - 자료 탐색: 다양한 관점에서 핵심 요소 파악
   - 문제 구조화: 개방형 질문 형태로 재구성

2. 아이디어 생성
   - 유창성, 유연성, 독창성 기반 다양한 아이디어 생성
   - 실행 가능성 높은 아이디어 선별

3. 실행 준비 (해결책 고안, 수용 구축)
   - 해결책 고안: 유망한 아이디어를 실행 가능한 해결책으로 구체화
   - 수용 구축: 실행 계획 및 어려움 극복 방법 고민

메타인지 요소:
- 점검(monitoring): 과제 특성 평가, 수행 예측, 아이디어 평가
- 조절(control): 전략 선택/변경, 과제 지속 여부, 해결안 선택
- 지식(knowledge): 이전 경험 활용, 새로운 학습 통합

단계별 질문 패턴:
1. 도전 이해: 지식 → 점검 → 조절 (반복)
2. 아이디어 생성: 점검 → 조절 (반복)
3. 실행 준비: 점검 → 조절 (반복) → 지식

원칙:
- 답변 제공 금지, 사고 촉진만
- 단계 이동 강요 금지
- 학습자 응답의 깊이 판단 후 다음 행동 결정
- 1-2문장의 간결한 질문만 생성

응답 형식:
JSON 형태로 다음 정보를 제공:
{
  "current_stage": "CPS 단계 (예: 도전_이해_자료탐색)",
  "detected_metacog_needs": ["필요한 메타인지 요소들"],
  "response_depth": "shallow|medium|deep",
  "scaffolding_question": "1-2문장의 촉진 질문",
  "should_transition": true|false,
  "reasoning": "판단 근거"
}
"""

    def generate_scaffolding(
        self,
        user_message: str,
        conversation_history: List[Dict[str, str]],
        current_stage: Optional[str] = None
    ) -> Dict:
        """
        Generate scaffolding question based on user message and conversation history

        Args:
            user_message: Current user message
            conversation_history: List of previous messages [{"role": "user"|"agent", "content": "..."}]
            current_stage: Current CPS stage if known

        Returns:
            Dictionary with scaffolding response including:
            - current_stage: Inferred CPS stage
            - detected_metacog_needs: List of metacognitive elements to address
            - response_depth: Assessment of response depth (shallow/medium/deep)
            - scaffolding_question: Question to promote thinking
            - should_transition: Whether to move to next CPS stage
            - reasoning: Explanation of decision
        """
        try:
            # Build conversation context
            context = self._build_context(conversation_history, current_stage)

            # Construct prompt
            prompt = f"""{self.system_prompt}

이전 대화:
{context}

학습자의 현재 응답: "{user_message}"

위 응답을 분석하여 JSON 형식으로 응답해주세요. 응답에는 반드시 current_stage, detected_metacog_needs, response_depth, scaffolding_question, should_transition, reasoning이 포함되어야 합니다."""

            # Generate response
            response = self.model.generate_content(prompt)
            result_text = response.text

            # Parse JSON response
            # Remove markdown code blocks if present
            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0].strip()
            elif "```" in result_text:
                result_text = result_text.split("```")[1].split("```")[0].strip()

            result = json.loads(result_text)

            logger.info(f"Generated scaffolding for stage: {result.get('current_stage')}")
            return result

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Gemini response as JSON: {e}")
            logger.error(f"Raw response: {result_text}")
            # Fallback response
            return self._create_fallback_response(user_message)

        except Exception as e:
            logger.error(f"Error generating scaffolding: {e}")
            return self._create_fallback_response(user_message)

    def _build_context(
        self,
        conversation_history: List[Dict[str, str]],
        current_stage: Optional[str]
    ) -> str:
        """Build conversation context string"""
        if not conversation_history:
            return "없음 (첫 대화)"

        context_parts = []
        for msg in conversation_history[-5:]:  # Last 5 messages
            role = "학습자" if msg["role"] == "user" else "에이전트"
            context_parts.append(f"{role}: {msg['content']}")

        if current_stage:
            context_parts.append(f"\n현재 단계: {current_stage}")

        return "\n".join(context_parts)

    def _create_fallback_response(self, user_message: str) -> Dict:
        """Create fallback response when Gemini fails"""
        return {
            "current_stage": "도전_이해_기회구성",
            "detected_metacog_needs": ["점검"],
            "response_depth": "medium",
            "scaffolding_question": "조금 더 구체적으로 설명해주시겠어요? 어떤 부분이 가장 중요하다고 생각하시나요?",
            "should_transition": False,
            "reasoning": "시스템 오류로 인한 기본 응답"
        }


# Global service instance
gemini_service = GeminiService()
