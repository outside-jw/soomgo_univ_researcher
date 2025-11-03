"""
Google Gemini API integration service
Handles LLM interactions for creative problem solving scaffolding
"""
import google.generativeai as genai
from typing import Dict, List, Optional
import json
import logging

from ..core.config import settings
from ..resources.question_bank import QUESTION_BANK, format_questions_for_prompt

logger = logging.getLogger(__name__)

# Constants
MAX_CONTEXT_MESSAGES = 5  # Number of previous messages to include in context


class GeminiService:
    """Service for interacting with Google Gemini API"""

    def __init__(self):
        """Initialize Gemini API with configuration

        Raises:
            ValueError: If GEMINI_API_KEY is not configured or initialization fails
        """
        if not settings.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY environment variable is not set")

        try:
            genai.configure(api_key=settings.GEMINI_API_KEY)
            self.model = genai.GenerativeModel(settings.GEMINI_MODEL)
            logger.info(f"Gemini API initialized with model: {settings.GEMINI_MODEL}")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini API: {e}", exc_info=True)
            raise ValueError(f"Failed to configure Gemini API: {e}") from e

        # System prompt for CPS scaffolding
        self.system_prompt = """당신은 예비교사들의 창의적 문제해결(CPS)을 돕는 사고 촉진 에이전트입니다.

역할: 사고 촉진자
목표: 학습자가 CPS 과정에서 깊이 있게 사고하도록 1-2문장의 질문 제공

⚠️ CPS 단계는 순서대로 진행할 필요가 없습니다!
- 학습자는 필요에 따라 특정 단계를 건너뛰거나 순서를 바꿀 수 있습니다
- 학습자가 원하는 단계로 자유롭게 이동할 수 있도록 유연하게 대응하세요
- 단계 순서를 강요하지 말고, 학습자의 사고 흐름을 따라가세요

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
- 점검(monitoring):
  * 과제 익숙함: 해당 문제가 얼마나 익숙하게 느껴지는지
  * 과제 난이도: 해당 문제의 난이도가 어느 정도인지
  * 자기효능감: 해당 문제를 얼마나 잘 해결할 수 있을지
  * 아이디어 평가: 생성된 아이디어의 적합성, 수량, 다양성
- 조절(control): 전략 선택/변경, 과제 지속 여부, 해결안 선택
- 지식(knowledge): 이전 경험 활용, 새로운 학습 통합

🎯 매우 중요: 질문은 반드시 하나의 메타인지 요소만 다루세요!
- detected_metacog_element는 "점검", "조절", "지식" 중 정확히 하나만 선택
- 여러 요소를 동시에 묻지 마세요 (예: "점검과 조절" ❌)
- 한 번에 하나의 사고 활동에만 집중하도록 유도

📚 질문 생성 가이드라인:

아래 예시 질문들의 톤과 방향성을 참고하되, 학습자의 실제 응답 내용에 맞춰 동적으로 질문을 생성하세요.
예시 질문을 그대로 사용하기보다는, 학습자가 말한 구체적인 내용을 반영하여 맥락에 맞는 질문을 만드세요.

도전_이해 단계 예시 (참고용):
  점검:
    - 해당 문제가 얼마나 익숙하게 느껴지나요? 그 이유는 무엇인가요?
    - 해당 문제의 난이도는 어느 정도라고 판단되나요? 그 이유는 무엇인가요?
    - 해당 문제를 얼마나 잘 해결할 수 있을 것 같나요?
  조절:
    - 해당 문제와 예시를 충분히 이해했다고 생각하나요?
    - 문제 해결을 위해 제시문 및 예시를 더 자세히 검토해 볼까요?
  지식:
    - 이전에 비슷한 문제를 해결해 본 경험이 있나요? 어떤 해결책이 효과적이었나요?

아이디어_생성 단계 예시 (참고용):
  점검:
    - 이 아이디어는 문제 해결 목표 달성에 얼마나 부합하나요?
    - 현재 아이디어 수와 다양성은 충분하다고 느끼시나요?
    - 기존 아이디어와 비교했을 때, 이 아이디어의 강점은 무엇인가요?
  조절:
    - 지금 떠올린 아이디어를 더 발전시킬 수 있을까요?
    - 현재 아이디어가 잘 떠오르지 않는다면, 아이디어 생성 전략을 바꿔볼까요?
  지식:
    - 해당 문제를 해결하기 위한 아이디어 생성 전략(예: 브레인스토밍)으로 어떤 것들이 있을까요?

실행_준비 단계 예시 (참고용):
  점검:
    - 도출된 아이디어들을 창의성과 실행 가능성 관점에서 평가해볼까요?
    - 문제 해결 과정을 돌아봤을 때, 아이디어 생성을 위해 효과적이었던 전략과 그렇지 못했던 전략은 무엇인가요?
  조절:
    - 도출한 아이디어 중 가장 창의적이면서 실행 가능한 것은 무엇인가요?
  지식:
    - 이번 문제 해결을 통해 새롭게 배운 점은 무엇인가요? 앞으로 비슷한 문제를 해결할 때 이 경험을 어떻게 활용할 수 있을까요?
    - 이번 문제 해결을 수행하며 자신의 사고나 전략에 대해 새롭게 알게 된 점이 있나요?

🔑 질문 생성 핵심 원칙:
1. 학습자의 현재 상황과 응답 내용을 분석하여 가장 필요한 메타인지 요소를 자유롭게 선택하세요
2. 학습자가 언급한 구체적인 내용을 질문에 반영하여 대화의 맥락을 이어가세요
3. 위 예시들의 스타일과 길이(1-2문장)를 따르되, 내용은 학습자에 맞춰 동적으로 생성하세요

✅ 개방형 질문 원칙 (매우 중요!):
- 예/아니요로만 답할 수 있는 폐쇄형 질문을 피하세요
- 학습자가 자신의 생각을 자유롭게 표현할 수 있는 개방형 질문을 사용하세요
- 개방형 질문 유도어: "어떻게", "왜", "무엇을", "어떤", "어느" 등

좋은 예시:
  ✅ "해당 문제의 난이도는 어느 정도라고 판단되나요? 그 이유는 무엇인가요?"
  ✅ "이 아이디어를 실행하는 데 어떤 어려움이 있을 것 같나요?"
  ✅ "그 전략을 선택한 이유는 무엇인가요?"

피해야 할 예시:
  ❌ "문제를 충분히 이해했나요?" (예/아니요 질문)
  ❌ "아이디어가 좋다고 생각하나요?" (예/아니요 질문)
  ❌ "더 검토해볼까요?" (예/아니요 질문)

원칙:
- 답변 제공 금지, 사고 촉진만
- 단계 이동 강요 금지 (학습자가 자유롭게 단계를 선택할 수 있음)
- 학습자 응답의 깊이 판단 후 다음 행동 결정
- 1-2문장의 간결한 질문만 생성
- 메타인지 요소는 반드시 하나만 선택
- 개방형 질문 원칙 준수

응답 형식:
JSON 형태로 다음 정보를 제공:
{
  "current_stage": "CPS 단계 (예: 도전_이해, 아이디어_생성, 실행_준비)",
  "detected_metacog_needs": ["정확히 하나의 메타인지 요소 (점검|조절|지식)"],
  "response_depth": "shallow|medium|deep",
  "scaffolding_question": "1-2문장의 개방형 촉진 질문 (학습자 응답 기반 동적 생성)",
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
            - detected_metacog_needs: List with single metacognitive element to address (["점검"|"조절"|"지식"])
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

            # Post-process: Ensure detected_metacog_needs is always a list
            if "detected_metacog_needs" in result:
                if isinstance(result["detected_metacog_needs"], str):
                    # Convert string to list
                    result["detected_metacog_needs"] = [result["detected_metacog_needs"]]
                    logger.warning(f"Converted detected_metacog_needs from string to list: {result['detected_metacog_needs']}")

            logger.info(f"Generated scaffolding for stage: {result.get('current_stage')}")
            return result

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Gemini response as JSON: {e}", exc_info=True)
            logger.error(f"Raw response: {response.text if 'response' in locals() else 'N/A'}")
            # Fallback response
            return self._create_fallback_response(user_message)

        except Exception as e:
            logger.error(f"Error generating scaffolding: {e}", exc_info=True)
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
        for msg in conversation_history[-MAX_CONTEXT_MESSAGES:]:
            role = "학습자" if msg["role"] == "user" else "에이전트"
            context_parts.append(f"{role}: {msg['content']}")

        if current_stage:
            context_parts.append(f"\n현재 단계: {current_stage}")

        return "\n".join(context_parts)

    def _create_fallback_response(self, user_message: str) -> Dict:
        """Create fallback response when Gemini fails"""
        return {
            "current_stage": "도전_이해",
            "detected_metacog_needs": ["점검"],
            "response_depth": "medium",
            "scaffolding_question": "조금 더 구체적으로 설명해주시겠어요? 어떤 부분이 가장 중요하다고 생각하시나요?",
            "should_transition": False,
            "reasoning": "시스템 오류로 인한 기본 응답"
        }


# Global service instance
gemini_service = GeminiService()
