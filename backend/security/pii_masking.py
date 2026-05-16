from presidio_analyzer.nlp_engine import SpacyNlpEngine
from presidio_analyzer import AnalyzerEngine, Pattern, PatternRecognizer
from presidio_anonymizer import AnonymizerEngine

# ── NLP 엔진 설정 (en_core_web_sm 사용) ──
nlp_engine = SpacyNlpEngine(models=[{"lang_code": "en", "model_name": "en_core_web_sm"}])
analyzer = AnalyzerEngine(nlp_engine=nlp_engine)
anonymizer = AnonymizerEngine()

# ── 한국 주민등록번호 전용 Recognizer ──
kr_rrn_recognizer = PatternRecognizer(
    supported_entity="KR_RRN",
    patterns=[Pattern("kr_rrn", regex=r"\d{6}-[1-4]\d{6}", score=0.9)]
)
analyzer.registry.add_recognizer(kr_rrn_recognizer)

# ── 한국 전화번호 전용 Recognizer ──
kr_phone_recognizer = PatternRecognizer(
    supported_entity="KR_PHONE_NUMBER",
    patterns=[Pattern("kr_phone", regex=r"01[016789]-\d{3,4}-\d{4}", score=0.85)]
)
analyzer.registry.add_recognizer(kr_phone_recognizer)


def mask_pii(text: str) -> str:
    """텍스트 내 모든 PII를 탐지하고 마스킹합니다.
    entities 파라미터를 생략하면 기본 영어 PII(이메일, 이름 등) +
    커스텀 한국어 PII를 모두 탐지합니다.
    """
    results = analyzer.analyze(text=text, language="en")
    anonymized = anonymizer.anonymize(text=text, analyzer_results=results)
    return anonymized.text
