import re
from dataclasses import dataclass
from typing import List


@dataclass
class SearchToken:
    """
    Represents a token used for searching.
    """

    token: str
    length: int = 0
    count: int = 0


class SearchMixin:
    """
    Utility mixin for indexing and searching documents.
    """

    _tokenizer_regex = re.compile(r'[\w\-]+')
    _tokenizer_wildcard_regex = re.compile(r'[\w\-*]+')

    def __init__(self, *args, max_tokens_length: int, **kwargs):
        super().__init__(*args, **kwargs)
        self.max_tokens_length = max_tokens_length

    def tokenize(self, content: str) -> List[SearchToken]:
        """
        Tokenize the content into search tokens.
        """
        extracted_tokens = []
        words = self._tokenizer_regex.findall(content.lower())

        for length in range(1, 1 + min(len(words), self.max_tokens_length)):
            indexed_tokens = {}

            # Extract tokens of the specified length
            tokens = [
                SearchToken(token=' '.join(words[i : i + length]), length=length)
                for i in range(len(words) - length + 1)
            ]

            # Aggregate token counts
            for token in tokens:
                if token.token not in indexed_tokens:
                    indexed_tokens[token.token] = SearchToken(
                        token=token.token, length=length
                    )
                indexed_tokens[token.token].count += 1

            extracted_tokens.extend(indexed_tokens.values())

        return extracted_tokens

    @classmethod
    def extract_search_terms(cls, query: str) -> List[str]:
        """
        Extract search terms from the query string.
        """
        terms = set()

        # lower+strip
        query = query.lower().strip()

        # Extract quoted terms (unless they have a trailing backslash)
        quoted_terms = re.findall(r'"([^"\\]*(?:\\.[^"\\]*)*)"', query)
        for term in quoted_terms:
            terms.add(term.strip())

            # Remove the quoted term from the query
            query = query.replace(f'"{term}"', '').strip()

        # Extract unquoted terms
        terms.update(cls._tokenizer_wildcard_regex.findall(query))
        return list(terms)
