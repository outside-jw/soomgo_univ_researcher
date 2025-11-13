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

        # System prompt for CPS scaffolding (질문 모드)
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

⭐ **핵심 인지 과정 질문 (최우선 사용)**:
- 각 CPS 단계로 **처음 전환될 때**, 반드시 해당 단계의 핵심 인지 과정 질문을 먼저 생성하세요
- 핵심 인지 과정 질문은 학습자가 **구체적인 산출물(아이디어/해결책)**을 만들도록 촉진합니다
- 단계 전환 직후가 아니라면, 메타인지 요소(점검/조절/지식) 기반 질문을 사용하세요

도전_이해 단계:
  🌟 핵심 인지 과정 (단계 시작 시 우선):
    - 현재 문제 속에서 어떤 요인들이 서로 영향을 주고받고 있나요?
    - 해당 문제를 한 문장으로 정의한다면 어떻게 표현할 수 있을까요?
    - 해당 문제를 동료교사나 학생의 관점에서 바라본다면 어떤 점이 다르게 보일까요?

  점검:
    - 해당 문제가 얼마나 익숙하게 느껴지나요? 그 이유는 무엇인가요?
    - 해당 문제의 난이도는 어느 정도라고 판단되나요? 그 이유는 무엇인가요?
    - 문제에서 가장 어려운 부분은 무엇인가요?
  조절:
    - 해당 문제와 예시를 충분히 이해했다고 생각하나요?
  지식:
    - 이전에 비슷한 문제를 해결해 본 경험이 있나요?

아이디어_생성 단계:
  🌟 핵심 인지 과정 (단계 시작 시 우선):
    - 문제를 해결할 수 있는 모든 아이디어를 자유롭게 떠올려볼까요?
    - 해당 아이디어를 제시한 이유나 근거는 무엇인가요?
    - 지금 떠올린 아이디어의 기대되는 효과나 한계를 설명해볼까요?

  점검:
    - 제시한 아이디어는 새로운 동시에 효과적인가요?
    - 지금까지 떠올린 아이디어 수나 다양성이 충분하다고 생각하시나요?
    - 다른 아이디어와 비교했을 때, 이 아이디어만의 강점은 무엇인가요?
  조절:
    - 지금 떠올린 아이디어를 더 발전시킬 수 있을까요?
  지식:
    - 해당 문제를 해결하기 위한 아이디어 생성 전략으로 어떤 것들이 있을까요?

실행_준비 단계:
  🌟 핵심 인지 과정 (단계 시작 시 우선):
    - 이 아이디어를 실제로 현장에서 실행한다면 어떤 결과나 변화가 발생할까요?
    - 아이디어 실행 과정에서 예상되는 어려움과 해결방안을 계획해볼까요?

  점검:
    - 도출된 아이디어들을 창의성과 실행 가능성 관점에서 평가해볼까요?
  조절:
    - 가장 창의적이면서 실행 가능한 아이디어를 골라볼까요?
  지식:
    - 이번 문제 해결을 통해 새롭게 배운 점은 무엇인가요?

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

📏 응답 깊이 평가 기준 (문자 수 기반):
- shallow: 40자 이하의 짧은 응답
- medium: 40~90자의 적절한 길이
- deep: 90자 이상의 긴 응답

💡 LLM 자율성:
- 학습자의 응답 깊이와 맥락을 종합적으로 고려하여 자율적으로 판단하세요
- 위 문자 수 기준을 참고하되, 응답의 내용과 품질도 함께 고려하세요
- Deep 응답이 2회 이상 나오면 다음 단계 전환을 고려할 수 있습니다

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

        # System prompt for answering mode (답변 모드)
        self.answer_prompt = """당신은 예비교사들의 창의적 문제해결(CPS)을 돕는 사고 촉진 에이전트입니다.

🔄 **양방향 상호작용 모드** - 학습자의 질문에 답변하기

학습자가 질문을 하거나 의견을 구할 때, 다음 범위 내에서 답변을 제공하세요:

✅ 답변 가능한 범위:
1. **방법론/접근법 설명**: CPS 방법론, 문제 해결 접근법, 사고 전략 등을 설명
   예: "CPS가 뭐예요?" → CPS 개념과 단계를 간단히 설명
   예: "어떻게 접근해야 하나요?" → 현재 단계에 적합한 접근 방법 안내

2. **예시 제공**: 유사한 상황이나 예시를 들어 이해를 돕기
   예: "구체적인 예시를 들어주세요" → 교육 현장의 유사 사례 제시

3. **피드백/격려**: 학습자의 아이디어나 생각에 대한 긍정적 피드백과 보완점 제시
   예: "이 아이디어 괜찮나요?" → "좋은 출발점입니다. 추가로 고려하면 좋을 점은..."

❌ 답변 불가능한 범위:
- **직접적인 해결책 제공**: 구체적인 정답이나 완성된 해결책을 제시하지 마세요
  예: "정답이 뭐예요?" → ❌ 정답 제공 대신, 스스로 찾아갈 수 있도록 질문으로 리다이렉트

💬 답변 원칙:
1. 1-3문장의 간결한 답변
2. 학습자의 사고를 촉진하는 방향으로 답변
3. 답변 후에도 추가로 생각해볼 점을 함께 제시
4. 여전히 scaffolding 원칙 유지 (사고 촉진자 역할)

응답 형식:
JSON 형태로 다음 정보를 제공:
{
  "current_stage": "현재 CPS 단계",
  "detected_metacog_needs": ["점검|조절|지식"],
  "response_depth": "shallow|medium|deep",
  "answer_message": "학습자 질문에 대한 답변 (1-3문장)",
  "follow_up_question": "답변 후 추가 사고를 촉진하는 질문 (선택사항)",
  "should_transition": false,
  "reasoning": "답변 제공 이유"
}
"""

    def _is_learner_question(self, message: str) -> bool:
        """
        Determine if the learner's message is a question requiring an answer

        Args:
            message: Learner's message

        Returns:
            True if the message is a question, False otherwise
        """
        # Check for question mark
        if '?' in message or '?' in message:
            return True

        # Check for common question patterns in Korean
        question_patterns = [
            '뭐예요', '뭔가요', '무엇인가요', '어떻게', '왜',
            '이유가', '설명해', '알려줘', '알려주세요',
            '괜찮나요', '맞나요', '좋나요', '어떤가요',
            '도와줘', '도와주세요', '의견', '생각'
        ]

        message_lower = message.lower()
        return any(pattern in message_lower for pattern in question_patterns)

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
            # Validate input
            if not user_message or not user_message.strip():
                logger.warning("Empty user message received")
                return self._create_fallback_response("(빈 메시지)")

            # Check if learner is asking a question (답변 모드 필요)
            is_question = self._is_learner_question(user_message)
            logger.info(f"Message type: {'QUESTION (답변 모드)' if is_question else 'STATEMENT (질문 모드)'}")

            # Build conversation context
            context = self._build_context(conversation_history, current_stage)

            # Select appropriate prompt based on message type
            if is_question:
                # 답변 모드: 학습자의 질문에 답변 제공
                system_prompt_to_use = self.answer_prompt
                instruction = """위 질문을 분석하여 JSON 형식으로 응답해주세요.
응답에는 반드시 current_stage, detected_metacog_needs, response_depth, answer_message, follow_up_question (선택), should_transition, reasoning이 포함되어야 합니다.

학습자의 질문에 대해 scaffolding 원칙을 유지하면서 도움이 되는 답변을 제공하세요."""
                message_label = "학습자의 질문"
            else:
                # 질문 모드: 기존 scaffolding 질문 생성
                system_prompt_to_use = self.system_prompt
                instruction = """위 응답을 분석하여 JSON 형식으로 응답해주세요.
응답에는 반드시 current_stage, detected_metacog_needs, response_depth, scaffolding_question, should_transition, reasoning이 포함되어야 합니다.

⚠️ 학습자가 "모르겠어", "잘 모르겠어요" 같은 불확실성을 표현하면, 더 구체적인 질문으로 사고를 촉진하세요."""
                message_label = "학습자의 현재 응답"

            # Construct prompt
            prompt = f"""{system_prompt_to_use}

이전 대화:
{context}

{message_label}: "{user_message}"

{instruction}"""

            # Generate response with timeout and error handling
            logger.info(f"Sending request to Gemini API for message: {user_message[:50]}...")
            response = self.model.generate_content(prompt)

            if not response or not response.text:
                logger.error("Gemini API returned empty response")
                return self._create_fallback_response(user_message)

            result_text = response.text
            logger.debug(f"Raw Gemini response (first 200 chars): {result_text[:200]}")

            # Parse JSON response
            # Remove markdown code blocks if present
            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0].strip()
            elif "```" in result_text:
                result_text = result_text.split("```")[1].split("```")[0].strip()

            result = json.loads(result_text)

            # Validate required fields based on mode
            if is_question:
                required_fields = ["current_stage", "detected_metacog_needs", "response_depth",
                                 "answer_message", "should_transition", "reasoning"]
                # Ensure we have answer_message and convert to scaffolding_question for consistency
                if "answer_message" in result:
                    # Combine answer with follow-up question if present
                    answer_text = result["answer_message"]
                    if "follow_up_question" in result and result["follow_up_question"]:
                        answer_text += " " + result["follow_up_question"]
                    result["scaffolding_question"] = answer_text
            else:
                required_fields = ["current_stage", "detected_metacog_needs", "response_depth",
                                 "scaffolding_question", "should_transition", "reasoning"]

            missing_fields = [field for field in required_fields if field not in result]
            if missing_fields:
                logger.error(f"Missing required fields in Gemini response: {missing_fields}")
                logger.error(f"Received result: {result}")
                return self._create_fallback_response(user_message)

            # Post-process: Ensure detected_metacog_needs is always a list
            if "detected_metacog_needs" in result:
                if isinstance(result["detected_metacog_needs"], str):
                    # Convert string to list
                    result["detected_metacog_needs"] = [result["detected_metacog_needs"]]
                    logger.warning(f"Converted detected_metacog_needs from string to list: {result['detected_metacog_needs']}")

                # Validate it's not empty
                if not result["detected_metacog_needs"]:
                    logger.warning("Empty detected_metacog_needs, setting default to '점검'")
                    result["detected_metacog_needs"] = ["점검"]

            logger.info(f"Successfully generated scaffolding for stage: {result.get('current_stage')}, depth: {result.get('response_depth')}")
            return result

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Gemini response as JSON: {e}", exc_info=True)
            logger.error(f"Raw response: {response.text if 'response' in locals() else 'N/A'}")
            # Fallback response
            return self._create_fallback_response(user_message)

        except AttributeError as e:
            logger.error(f"Gemini API response format error: {e}", exc_info=True)
            return self._create_fallback_response(user_message)

        except Exception as e:
            logger.error(f"Unexpected error generating scaffolding: {e}", exc_info=True)
            logger.error(f"User message: {user_message}")
            logger.error(f"Conversation history length: {len(conversation_history)}")
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
        """Create fallback response when Gemini fails

        Provides a safe, general scaffolding question that can work in any situation.
        """
        logger.warning(f"Using fallback response for message: {user_message[:100]}")

        # Different fallbacks based on message length
        if len(user_message.strip()) < 10:
            question = "조금 더 구체적으로 설명해주시겠어요? 어떤 상황인지 말씀해주세요."
        else:
            question = "말씀해주신 내용에 대해 조금 더 자세히 이야기해볼까요? 어떤 부분이 가장 중요하다고 생각하시나요?"

        return {
            "current_stage": "도전_이해",
            "detected_metacog_needs": ["점검"],
            "response_depth": "medium",
            "scaffolding_question": question,
            "should_transition": False,
            "reasoning": "시스템 오류로 인한 안전한 기본 응답 제공"
        }


# Global service instance
gemini_service = GeminiService()
