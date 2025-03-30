from abc import ABC, abstractmethod

import langdetect


class InvalidLlmInputException(Exception):
    pass


class InvalidLlmResponseException(Exception):
    pass


class InputGuardrail(ABC):
    @abstractmethod
    def evaluate(self, llm_input: str):
        raise NotImplementedError()


class OutputGuardrail(ABC):
    @abstractmethod
    def evaluate(self, llm_response: str):
        raise NotImplementedError()


class SufficientTextGuardrail(InputGuardrail):
    def evaluate(self, llm_input: str):
        if len(llm_input) < 20:
            raise InvalidLlmInputException(f"Not enough text to process, received only {len(llm_input)} characters")


class TranslatedGuardrail(OutputGuardrail):
    def evaluate(self, llm_response: str):
        lang = langdetect.detect(llm_response)
        # Yes, lots of non-English languages use ascii-compatible letters. This is just a quick check.
        if not llm_response.isascii() and lang != 'en':
            raise InvalidLlmResponseException(
                f"Language of LLM response contains non-ascii letters, detected language: {lang}")


class PreambleGuardrail(OutputGuardrail):
    def evaluate(self, llm_response: str):
        if 'certainly' in llm_response.lower():
            raise InvalidLlmResponseException(
                "LLM response includes the word 'certainly', which is typically extraneous")


class OutputFormatCheckerGuardrail(OutputGuardrail):
    def __init__(self, expected_lines: int):
        self.expected_lines = expected_lines

    def evaluate(self, llm_response: str):
        lines = [line for line in llm_response.splitlines() if len(line.strip()) > 0]
        if len(lines) < self.expected_lines:
            raise InvalidLlmResponseException(f"Response contained {len(lines)} lines, expected {self.expected_lines}")
