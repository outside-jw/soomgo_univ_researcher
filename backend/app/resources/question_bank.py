"""
질문 뱅크 (Question Bank)

scaffolding.md에서 추출한 모든 예시 질문들을 CPS 단계와 메타인지 요소별로 구조화
각 질문은 실제 사용 시 그대로 제공되어야 함 (Gemini가 새로 생성하지 않음)
"""

QUESTION_BANK = {
    # 도전(문제) 이해 단계
    "도전_이해": {
        "조절": [
            "해당 문제와 예시를 충분히 이해했다고 생각하나요?",
            "문제 해결을 위해 제시문 및 예시를 더 자세히 검토해 볼까요?",
        ],
        "점검": [
            "해당 문제가 얼마나 익숙하게 느껴지나요? 그 이유는 무엇인가요?",
            "해당 문제의 난이도는 어느 정도라고 판단되나요? 그 이유는 무엇인가요?",
            "해당 문제를 얼마나 잘 해결할 수 있을 것 같나요?",
        ],
        "지식": [
            "이전에 비슷한 문제를 해결해 본 경험이 있나요? 어떤 해결책이 효과적이었나요?",
        ],
    },

    # 아이디어 생성 단계
    "아이디어_생성": {
        "조절": [
            "지금 떠올린 아이디어를 더 발전시킬 수 있을까요?",
            "현재 아이디어가 잘 떠오르지 않는다면, 아이디어 생성 전략을 바꿔볼까요?",
        ],
        "점검": [
            "이 아이디어는 문제 해결 목표 달성에 얼마나 부합하나요?",
            "현재 아이디어 수와 다양성은 충분하다고 느끼시나요?",
            "기존 아이디어와 비교했을 때, 이 아이디어의 강점은 무엇인가요?",
        ],
        "지식": [
            "해당 문제를 해결하기 위한 아이디어 생성 전략(예: 브레인스토밍)으로 어떤 것들이 있을까요? 가장 효과적이라고 판단되는 전략을 선택해 아이디어를 생성해볼까요?",
        ],
    },

    # 실행 준비 단계
    "실행_준비": {
        "조절": [
            "도출한 아이디어 중 가장 창의적이면서 실행 가능한 것은 무엇인가요?",
        ],
        "점검": [
            "도출된 아이디어들을 창의성과 실행 가능성 관점에서 평가해볼까요?",
            "문제 해결 과정을 돌아봤을 때, 아이디어 생성을 위해 효과적이었던 전략과 그렇지 못했던 전략은 무엇인가요?",
        ],
        "지식": [
            "이번 문제 해결을 통해 새롭게 배운 점은 무엇인가요? 앞으로 비슷한 문제를 해결할 때 이 경험을 어떻게 활용할 수 있을까요?",
            "이번 문제 해결을 수행하며 자신의 사고나 전략에 대해 새롭게 알게 된 점이 있나요?",
        ],
    },
}


def get_question(stage: str, metacog_element: str, index: int = 0) -> str:
    """
    특정 CPS 단계와 메타인지 요소에 해당하는 질문을 반환

    Args:
        stage: CPS 단계 ("도전_이해", "아이디어_생성", "실행_준비")
        metacog_element: 메타인지 요소 ("점검", "조절", "지식")
        index: 질문 인덱스 (기본값: 0, 첫 번째 질문)

    Returns:
        해당하는 질문 문자열, 없으면 빈 문자열
    """
    try:
        questions = QUESTION_BANK.get(stage, {}).get(metacog_element, [])
        if questions and 0 <= index < len(questions):
            return questions[index]
        return ""
    except Exception:
        return ""


def get_all_questions(stage: str, metacog_element: str) -> list[str]:
    """
    특정 CPS 단계와 메타인지 요소에 해당하는 모든 질문을 반환

    Args:
        stage: CPS 단계 ("도전_이해", "아이디어_생성", "실행_준비")
        metacog_element: 메타인지 요소 ("점검", "조절", "지식")

    Returns:
        질문 문자열 리스트
    """
    return QUESTION_BANK.get(stage, {}).get(metacog_element, [])


def get_random_question(stage: str, metacog_element: str) -> str:
    """
    특정 CPS 단계와 메타인지 요소에 해당하는 질문을 랜덤으로 선택하여 반환

    Args:
        stage: CPS 단계 ("도전_이해", "아이디어_생성", "실행_준비")
        metacog_element: 메타인지 요소 ("점검", "조절", "지식")

    Returns:
        랜덤으로 선택된 질문 문자열, 없으면 빈 문자열
    """
    import random
    questions = get_all_questions(stage, metacog_element)
    return random.choice(questions) if questions else ""


def format_questions_for_prompt(stage: str) -> str:
    """
    특정 CPS 단계의 모든 질문을 시스템 프롬프트용으로 포맷팅

    Args:
        stage: CPS 단계 ("도전_이해", "아이디어_생성", "실행_준비")

    Returns:
        포맷팅된 질문 목록 문자열
    """
    if stage not in QUESTION_BANK:
        return ""

    formatted = []
    stage_data = QUESTION_BANK[stage]

    for metacog in ["점검", "조절", "지식"]:
        if metacog in stage_data and stage_data[metacog]:
            formatted.append(f"\n{metacog}:")
            for i, question in enumerate(stage_data[metacog], 1):
                formatted.append(f"  {i}. {question}")

    return "\n".join(formatted)
