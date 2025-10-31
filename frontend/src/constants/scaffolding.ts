/**
 * Scaffolding purpose and characteristics mapping
 * Based on scaffolding.md documentation
 */

// Metacognition element descriptions
export const METACOG_DESCRIPTIONS: Record<string, string> = {
  '점검': '과제를 평가하고 자신의 수행을 점검합니다',
  '조절': '전략을 선택하고 과제를 조절합니다',
  '지식': '이전 경험과 지식을 활용합니다',
};

// Stage category mapping
const STAGE_CATEGORIES: Record<string, string> = {
  '도전_이해_기회구성': '도전_이해',
  '도전_이해_자료탐색': '도전_이해',
  '도전_이해_문제구조화': '도전_이해',
  '아이디어_생성': '아이디어_생성',
  '실행_준비_해결책고안': '실행_준비',
  '실행_준비_수용구축': '실행_준비',
};

// Scaffolding purpose by stage category and metacognition element
export const SCAFFOLDING_PURPOSES: Record<string, Record<string, string>> = {
  '도전_이해': {
    '점검': '과제 특성 평가 · 수행 예측',
    '조절': '과제 참여 판단 · 자원 활용 결정',
    '지식': '이전 경험 활용 · 유사 문제 해결 경험',
  },
  '아이디어_생성': {
    '점검': '아이디어 후보 평가 · 진행 평가',
    '조절': '전략 선택/변경 · 아이디어 판단',
    '지식': '메타인지 지식 인출 · 생성 전략 활용',
  },
  '실행_준비': {
    '점검': '전체 수행 평가 · 창의성 검토',
    '조절': '창의적 아이디어 선택 · 해결안 결정',
    '지식': '메타인지 지식 갱신 · 학습 성찰',
  },
};

/**
 * Get scaffolding purpose description for a given stage and metacognition element
 */
export function getScaffoldingPurpose(stage: string, metacogElement: string): string {
  const category = STAGE_CATEGORIES[stage];
  if (!category) return METACOG_DESCRIPTIONS[metacogElement] || '';

  return SCAFFOLDING_PURPOSES[category]?.[metacogElement] || METACOG_DESCRIPTIONS[metacogElement] || '';
}

/**
 * Stage transition messages
 */
export const STAGE_TRANSITION_MESSAGES: Record<string, string> = {
  '도전_이해_기회구성': '기회를 충분히 탐색했습니다',
  '도전_이해_자료탐색': '자료를 잘 탐색했습니다',
  '도전_이해_문제구조화': '문제를 명확히 구조화했습니다',
  '아이디어_생성': '다양한 아이디어를 생성했습니다',
  '실행_준비_해결책고안': '실행 가능한 해결책을 마련했습니다',
  '실행_준비_수용구축': '구체적인 실행 계획을 세웠습니다',
};

/**
 * Next stage names for transitions
 */
export const NEXT_STAGE_NAMES: Record<string, string> = {
  '도전_이해_기회구성': '자료 탐색',
  '도전_이해_자료탐색': '문제 구조화',
  '도전_이해_문제구조화': '아이디어 생성',
  '아이디어_생성': '해결책 고안',
  '실행_준비_해결책고안': '수용 구축',
  '실행_준비_수용구축': '완료',
};
