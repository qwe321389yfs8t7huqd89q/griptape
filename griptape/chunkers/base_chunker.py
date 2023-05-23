from abc import ABC
from typing import Optional, Union
from attr import define, field, Factory
from griptape.artifacts import TextArtifact
from griptape.chunkers import ChunkSeparator
from griptape.tokenizers import TiktokenTokenizer


@define
class BaseChunker(ABC):
    DEFAULT_SEPARATORS = [
        ChunkSeparator(" ")
    ]

    separators: list[ChunkSeparator] = field(
        default=Factory(lambda self: self.DEFAULT_SEPARATORS, takes_self=True),
        kw_only=True
    )
    tokenizer: TiktokenTokenizer = field(
        default=TiktokenTokenizer(),
        kw_only=True
    )
    max_tokens_per_chunk: int = field(
        default=Factory(lambda self: self.tokenizer.max_tokens, takes_self=True),
        kw_only=True
    )

    def chunk(self, chunk: Union[TextArtifact, str]) -> list[TextArtifact]:
        return self._chunk_recursively(chunk)

    def _chunk_recursively(
            self, chunk: Union[TextArtifact, str], current_separator: Optional[ChunkSeparator] = None
    ) -> list[TextArtifact]:
        chunk = chunk.value if isinstance(chunk, TextArtifact) else chunk
        token_count = self.tokenizer.token_count(chunk)

        if token_count <= self.max_tokens_per_chunk:
            return [TextArtifact(chunk)]
        else:
            balance_index = -1
            balance_diff = float("inf")
            tokens_count = 0
            half_token_count = token_count // 2

            if current_separator:
                separators = self.separators[self.separators.index(current_separator):]
            else:
                separators = self.separators

            for separator in separators:
                subchanks = list(filter(None, chunk.split(separator.value)))

                if len(subchanks) > 1:
                    for index, subchunk in enumerate(subchanks):
                        if index < len(subchanks):
                            if separator.is_prefix:
                                subchunk = separator.value + subchunk
                            else:
                                subchunk = subchunk + separator.value

                        tokens_count += self.tokenizer.token_count(subchunk)

                        if abs(tokens_count - half_token_count) < balance_diff:
                            balance_index = index
                            balance_diff = abs(tokens_count - half_token_count)

                    if separator.is_prefix:
                        first_subchunk = separator.value + separator.value.join(subchanks[:balance_index + 1])
                    else:
                        first_subchunk = separator.value.join(subchanks[:balance_index + 1]) + separator.value

                    second_subchunk = separator.value.join(subchanks[balance_index + 1:])

                    first_subchunk_rec = self._chunk_recursively(first_subchunk.strip(), separator)
                    second_subchunk_rec = self._chunk_recursively(second_subchunk.strip(), separator)

                    if first_subchunk_rec and second_subchunk_rec:
                        return first_subchunk_rec + second_subchunk_rec
                    elif first_subchunk_rec:
                        return first_subchunk_rec
                    elif second_subchunk_rec:
                        return second_subchunk_rec
                    else:
                        return []
            return []
