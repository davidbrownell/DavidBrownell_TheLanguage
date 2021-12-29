# ----------------------------------------------------------------------
# |
# |  This file has been automatically generated by PythonVisitor.py.
# |
# ----------------------------------------------------------------------


import copy
from enum import auto, Enum

from CommonEnvironmentEx.Package import InitRelativeImports

with InitRelativeImports():
    from ...CommonLibrary import HashLib_TheLanguage as HashLib
    from ...CommonLibrary.Int_TheLanguage import *
    from ...CommonLibrary.List_TheLanguage import List
    # from ...CommonLibrary.Num_TheLanguage import Num
    # from ...CommonLibrary.Queue_TheLanguage import Queue
    from ...CommonLibrary.Range_TheLanguage import *
    from ...CommonLibrary.Set_TheLanguage import Set
    from ...CommonLibrary.Stack_TheLanguage import Stack
    from ...CommonLibrary.String_TheLanguage import String

    from ..Components_TheLanguage.Phrase_TheLanguage import Phrase, NormalizedIterator
    from ..Components_TheLanguage.Token_TheLanguage import DedentToken, IndentToken, NewlineToken, RegexToken, Token

# Visibility: public
# ClassModifier: mutable
# ClassType: Class
class TokenPhrase(Phrase):
    def __init__(self, *args, **kwargs):
        args = list(args)
        TokenPhrase._InternalInit(self, args, kwargs)
        assert not args, args
        assert not kwargs, kwargs

    def _InternalInit(self, args, kwargs):
        # token

        Phrase._InternalInit(self, args, kwargs)

        # token
        if "token" in kwargs:
            self.token = kwargs.pop("token")
        elif args:
            self.token = args.pop(0)
        else:
            raise Exception("token was not provided")

        self._Init_6539f27a278a4c16a316d344d033ab3e_()

    def __eq__(self, other):
        compare_cache = {}

        if Phrase.__eq__(self, other) is False: return False
        if not isinstance(other, self.__class__): return False
        return self.__class__.__Compare__(self, other, compare_cache) == 0

    def __ne__(self, other):
        compare_cache = {}

        if Phrase.__ne__(self, other) is False: return False
        if not isinstance(other, self.__class__): return True
        return self.__class__.__Compare__(self, other, compare_cache) != 0

    def __lt__(self, other):
        compare_cache = {}

        if Phrase.__lt__(self, other) is False: return False
        if not isinstance(other, self.__class__): return False
        return self.__class__.__Compare__(self, other, compare_cache) < 0

    def __le__(self, other):
        compare_cache = {}

        if Phrase.__le__(self, other) is False: return False
        if not isinstance(other, self.__class__): return False
        return self.__class__.__Compare__(self, other, compare_cache) <= 0

    def __gt__(self, other):
        compare_cache = {}

        if Phrase.__gt__(self, other) is False: return False
        if not isinstance(other, self.__class__): return False
        return self.__class__.__Compare__(self, other, compare_cache) > 0

    def __ge__(self, other):
        compare_cache = {}

        if Phrase.__ge__(self, other) is False: return False
        if not isinstance(other, self.__class__): return False
        return self.__class__.__Compare__(self, other, compare_cache) >= 0

    @classmethod
    def __Compare__(cls, a, b, compare_cache):
        result = Phrase.__Compare__(a, b, compare_cache)
        if result != 0: return result

        result = cls.__CompareItem__(a.token, b.token, compare_cache)
        if result is not None: return result

        return 0

    @classmethod
    def __CompareItem__(cls, a, b, compare_cache):
        cache_key = (id(a), id(b), )

        cache_value = compare_cache.get(cache_key, None)
        if cache_value is not None:
            return cache_value

        def Impl():
            nonlocal a
            nonlocal b

            if a is None and b is None:
                return None

            if a is None: return -1
            if b is None: return 1

            try:
                if a < b: return -1
                if a > b: return 1
            except TypeError:
                a = id(a)
                b = id(b)

                if a < b: return -1
                if a > b: return 1

            return None

        result = Impl()

        compare_cache[cache_key] = result
        return result

    def _Init_6539f27a278a4c16a316d344d033ab3e_(self):
        pass

    @property
    def Token(self): return self.token
    # Return Type: TokenPhrase
    @staticmethod
    def Create(token, name=None, ):
        if name is None:
            name = token.name

        return TokenPhrase(name, token, )

    # Return Type: <LexResult | None> val
    def Lex(self, unique_id, iter, observer, ignore_whitespace=False, ):
        LexResult = Phrase.LexResult
        NormalizedIteratorRange = Phrase.NormalizedIteratorRange
        PhraseLexResultData = Phrase.PhraseLexResultData
        TokenLexResultData = Phrase.TokenLexResultData
        result = None # as <Token_MatchResult | None>
        observer.StartPhrase(unique_id, self, )
        result = self.token.Match_(iter.Clone(), )
        if result is None:
            observer.EndPhrase(unique_id, self, result is not None)
            iter_clone = iter.Clone()
            return LexResult(False, NormalizedIteratorRange(iter_clone, iter_clone, ), PhraseLexResultData(self, None, None, ), )

        iter_range = NormalizedIteratorRange(iter, result.iterator, )
        data = PhraseLexResultData(self, TokenLexResultData(self.token, result, iter_range, is_ignored=self.token.is_always_ignored, ), unique_id, )
        if self.token.__class__.__name__ == "IndentToken":
            observer.OnPushScopeProxy(data, iter_range, )
        elif self.token.__class__.__name__ == "DedentToken":
            observer.OnPopScopeProxy(data, iter_range, )
        elif not observer.OnInternalPhraseProxy(data, iter_range, ):
            return None

        observer.EndPhrase(unique_id, self, result is not None)
        return LexResult(True, iter_range, data, )

    # Return Type: Bool val
    def _PopulateRecursiveImpl(self, new_phrase, ):
        return False

    from typing import List, Optional, Tuple
    _indent_token                           = IndentToken.Create()
    _dedent_token                           = DedentToken.Create()
    _newline_token                          = NewlineToken.Create()
    # TODO: Caching opportunity
    @classmethod
    def ExtractPotentialCommentsOrWhitespace(
        cls,
        comment_token: RegexToken,
        normalized_iter: Phrase.NormalizedIterator,
        ignored_indentation_level: Optional[int],
        *,
        ignore_whitespace: bool,
        next_phrase_is_indent: bool,
        next_phrase_is_dedent: bool,
    ) -> Optional[
        Tuple[
            List[Phrase.TokenLexResultData],
            Phrase.NormalizedIterator,
            Optional[int],                              # Updated 'ignored_indentation_level' value
        ]
    ]:
        # Note that this should only be invoked on a phrase associated with a token that represents
        # a comment.
        data_items: List[Phrase.TokenLexResultData] = []
        while not normalized_iter.AtEnd():
            if ignore_whitespace:
                process_whitespace = True
                consume_indent = True
                consume_dedent = ignored_indentation_level != 0
            elif normalized_iter.Offset == 0:
                # If we are at the beginning of the content, consume any leading
                # newlines. We don't need to worry about a content that starts with
                # newline-comment-newline as the comment extract code will handle
                # the newline(s) that appears after the comment.
                process_whitespace = True
                consume_indent = False
                consume_dedent = False
            else:
                process_whitespace = False
                consume_indent = False
                consume_dedent = False
            if process_whitespace:
                data_item = cls.ExtractPotentialWhitespaceToken(
                    normalized_iter,
                    consume_indent=consume_indent,
                    consume_dedent=consume_dedent,
                    consume_newline=True,
                )
                if data_item is not None:
                    if ignored_indentation_level is not None:
                        if isinstance(data_item.Token, IndentToken):
                            ignored_indentation_level += 1
                        elif isinstance(data_item.Token, DedentToken):
                            assert ignored_indentation_level
                            ignored_indentation_level -= 1
                    data_items.append(data_item)
                    normalized_iter = data_item.IterEnd.Clone()
                    continue
            # Check for comments
            potential_comment_items = cls._ExtractPotentialCommentTokens(
                comment_token,
                normalized_iter,
                next_phrase_is_indent=next_phrase_is_indent,
                next_phrase_is_dedent=next_phrase_is_dedent,
            )
            if potential_comment_items is not None:
                potential_comment_items, normalized_iter = potential_comment_items
                data_items += potential_comment_items
                continue
            # If here, we didn't find anything
            break
        if not data_items:
            return None
        return (data_items, normalized_iter, ignored_indentation_level)
    # ----------------------------------------------------------------------
    # TODO: Caching opportunity
    @staticmethod
    def ExtractPotentialWhitespace(
        normalized_iter: Phrase.NormalizedIterator,
    ) -> Optional[Tuple[int, int]]:
        """Consumes any whitespace located at the current offset"""
        if normalized_iter.AtEnd():
            return None
        next_token_type = normalized_iter.GetNextTokenType()
        if next_token_type == Phrase.NormalizedIterator.TokenType.WhitespacePrefix:
            normalized_iter.SkipWhitespacePrefix()
        elif (
            next_token_type == Phrase.NormalizedIterator.TokenType.Content
            or next_token_type == Phrase.NormalizedIterator.TokenType.WhitespaceSuffix
        ):
            start = normalized_iter.Offset
            while (
                normalized_iter.Offset < normalized_iter.LineInfo.OffsetEnd
                and normalized_iter.Content[normalized_iter.Offset].isspace()
                and normalized_iter.Content[normalized_iter.Offset] != "\n"
            ):
                normalized_iter.Advance(1)
            if normalized_iter.Offset != start:
                return start, normalized_iter.Offset
        return None
    # ----------------------------------------------------------------------
    # TODO: Caching opportunity
    @classmethod
    def _ExtractPotentialCommentTokens(
        cls,
        comment_token: RegexToken,
        normalized_iter: Phrase.NormalizedIterator,
        *,
        next_phrase_is_indent: bool,
        next_phrase_is_dedent: bool,
    ) -> Optional[Tuple[List[Phrase.TokenLexResultData], Phrase.NormalizedIterator]]:
        """Eats any comment (stand-along or trailing) when requested"""
        normalized_iter = normalized_iter.Clone()
        next_token_type = normalized_iter.GetNextTokenType()
        if next_token_type == Phrase.NormalizedIterator.TokenType.Indent:
            # There are 2 scenarios to consider here:
            #
            #     1) The indent that we are looking at is because the comment itself
            #        is indented. Example:
            #
            #           Line 1: Int value = 1       # The first line of the comment
            #           Line 2:                     # The second line of the comment
            #           Line 3: value += 1
            #
            #        In this scenario, Line 2 starts with an indent and Line 3 starts with
            #        a dedent. We want to consume and ignore both the indent and dedent.
            #
            #     2) The indent is a meaningful part of the statement. Example:
            #
            #           Line 1: class Foo():
            #           Line 2:     # A comment
            #           Line 3:     Int value = 1
            #
            #        In this scenario, Line 2 is part of the class declaration and we want
            #        the indent to be officially consumed before we process the comment.
            if next_phrase_is_indent:
                # We are in scenario #2
                return None
            # If here, we are in scenario #1
            at_beginning_of_line = True
            normalized_iter_offset = normalized_iter.Offset
            normalized_iter.SkipWhitespacePrefix()
            assert normalized_iter.Offset > normalized_iter_offset
            potential_whitespace = (normalized_iter_offset, normalized_iter.Offset)
        elif next_token_type == Phrase.NormalizedIterator.TokenType.WhitespacePrefix:
            at_beginning_of_line = True
            normalized_iter.SkipWhitespacePrefix()
            potential_whitespace = None
        else:
            at_beginning_of_line = (
                normalized_iter.Offset == normalized_iter.LineInfo.OffsetStart
                or normalized_iter.Offset == normalized_iter.LineInfo.ContentStart
            )
            potential_whitespace = cls.ExtractPotentialWhitespace(normalized_iter)
        normalized_iter_begin = normalized_iter.Clone()
        result = comment_token.Match_(normalized_iter)
        if result is None:
            return None
        results = [
            # pylint: disable=too-many-function-args
            Phrase.TokenLexResultData(
                comment_token,
                result,
                Phrase.NormalizedIteratorRange(normalized_iter_begin, normalized_iter),
                is_ignored=True,
            ),
        ]
        if at_beginning_of_line:
            # Add additional content to consume the entire line...
            # Capture the trailing newline
            result = cls.ExtractPotentialWhitespaceToken(
                results[-1].IterEnd,
                consume_indent=False,
                consume_dedent=False,
                consume_newline=True,
            )
            assert result
            results.append(result)
            # Consume potential dedents, but don't return it with the results (as we absorbed the
            # corresponding indent above when we skipped the prefix). We need to do this as every
            # dedent must have a matching indent token.
            if (
                results[0].Whitespace is not None
                and results[-1].IterEnd.GetNextTokenType() == Phrase.NormalizedIterator.TokenType.Dedent
                and not next_phrase_is_dedent
            ):
                result = cls.ExtractPotentialWhitespaceToken(
                    results[-1].IterEnd,
                    consume_indent=False,
                    consume_dedent=True,
                    consume_newline=False,
                )
                assert result
                # Even though we aren't sending the dedent token, we need to make sure that the returned
                # iterator is updated to the new position. Comments are special beasts.
                return (results, result.IterEnd)
        return (results, results[-1].IterEnd)
    # ----------------------------------------------------------------------
    # TODO: Caching opportunity
    @classmethod
    def ExtractPotentialWhitespaceToken(
        cls,
        normalized_iter: Phrase.NormalizedIterator,
        *,
        consume_indent: bool,
        consume_dedent: bool,
        consume_newline: bool,
    ) -> Optional[Phrase.TokenLexResultData]:
        """Eats any whitespace token when requested"""
        next_token_type = normalized_iter.GetNextTokenType()
        if next_token_type == Phrase.NormalizedIterator.TokenType.Indent:
            if not consume_indent:
                return None
            normalized_iter_begin = normalized_iter.Clone()
            result = cls._indent_token.Match_(normalized_iter)
            assert result
            # pylint: disable=too-many-function-args
            return Phrase.TokenLexResultData(
                cls._indent_token,
                result,
                Phrase.NormalizedIteratorRange(normalized_iter_begin, normalized_iter),
                is_ignored=True,
            )
        elif next_token_type == Phrase.NormalizedIterator.TokenType.Dedent:
            if not consume_dedent:
                return None
            normalized_iter_begin = normalized_iter.Clone()
            result = cls._dedent_token.Match_(normalized_iter)
            assert result
            # pylint: disable=too-many-function-args
            return Phrase.TokenLexResultData(
                cls._dedent_token,
                result,
                Phrase.NormalizedIteratorRange(normalized_iter_begin, normalized_iter),
                is_ignored=True,
            )
        # Consume potential newlines
        if consume_newline:
            normalized_iter = normalized_iter.Clone()
            normalized_iter_begin = normalized_iter.Clone()
            if next_token_type == Phrase.NormalizedIterator.TokenType.EndOfLine:
                potential_whitespace = None
            else:
                potential_whitespace = cls.ExtractPotentialWhitespace(normalized_iter)
            if normalized_iter.GetNextTokenType() == Phrase.NormalizedIterator.TokenType.EndOfLine:
                result = cls._newline_token.Match_(normalized_iter)
                assert result
                # pylint: disable=too-many-function-args
                return Phrase.TokenLexResultData(
                    cls._newline_token,
                    result,
                    Phrase.NormalizedIteratorRange(normalized_iter_begin, normalized_iter),
                    is_ignored=True,
                )
        return None
