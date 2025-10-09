"""
Гибридный поиск для религиозных текстов
Реализация схемы от AI агента по настройке ИИ
"""

import re
import math
import json
import logging
from typing import List, Dict, Any, Tuple, Set
from collections import Counter, defaultdict
from dataclasses import dataclass
import numpy as np
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

@dataclass
class SearchResult:
    """Результат поиска с детальной информацией"""
    id: int
    text: str
    book_name: str
    author: str
    confession: str
    theme: str
    score: float
    score_breakdown: Dict[str, float]  # Детализация по компонентам
    boosts_applied: List[str]  # Какие бусты применены

class QueryRewriter:
    """Переписывание запроса с синонимами и темами"""
    
    def __init__(self):
        self.synonyms = {
            # Храм/Церковь
            'храм': ['церковь', 'собор', 'богослужение', 'литургия', 'мечеть', 'намаз'],
            'церковь': ['храм', 'собор', 'богослужение', 'литургия'],
            'мечеть': ['храм', 'намаз', 'богослужение'],
            
            # Семья/Брак
            'жена': ['супруга', 'брак', 'семья', 'семейный'],
            'измена': ['прелюбодеяние', 'неверность', 'развод', 'прощение', 'покаяние'],
            'брак': ['семья', 'супружество', 'женитьба'],
            
            # Апокалипсис/Конец света
            'апокалипсис': ['конец света', 'второе пришествие', 'страшный суд', 'эсхатология'],
            'конец света': ['апокалипсис', 'второе пришествие', 'страшный суд', 'эсхатология'],
            'второе пришествие': ['апокалипсис', 'конец света', 'страшный суд'],
            
            # Молитва/Поклонение
            'молитва': ['намаз', 'поклонение', 'дуа', 'мольба'],
            'намаз': ['молитва', 'поклонение', 'салят'],
            
            # Бог/Аллах
            'бог': ['аллах', 'господь', 'творец', 'всевышний'],
            'аллах': ['бог', 'господь', 'творец', 'всевышний'],
            
            # Истина/Правда
            'истина': ['правда', 'истинность', 'достоверность'],
            'правда': ['истина', 'истинность', 'достоверность'],
        }
        
        self.themes = {
            'храм': ['богослужение', 'литургия', 'таинства', 'воскресенье', 'праздник'],
            'семья': ['брак', 'супружество', 'дети', 'родители', 'родственники'],
            'молитва': ['поклонение', 'дуа', 'намаз', 'богослужение'],
            'апокалипсис': ['эсхатология', 'пророчества', 'признаки', 'суд'],
            'измена': ['верность', 'прелюбодеяние', 'развод', 'прощение'],
        }
    
    def normalize_text(self, text: str) -> str:
        """Нормализация текста"""
        # Приводим к нижнему регистру
        text = text.lower()
        # Удаляем пунктуацию, оставляем только буквы и пробелы
        text = re.sub(r'[^\w\s]', ' ', text)
        # Убираем лишние пробелы
        text = re.sub(r'\s+', ' ', text).strip()
        return text
    
    def expand_query(self, query: str) -> Tuple[List[str], List[str]]:
        """Расширение запроса синонимами и темами"""
        normalized = self.normalize_text(query)
        words = normalized.split()
        
        # Основные слова запроса
        main_words = words.copy()
        
        # Добавляем синонимы
        synonyms = []
        for word in words:
            if word in self.synonyms:
                synonyms.extend(self.synonyms[word])
        
        # Добавляем темы
        themes = []
        for word in words:
            if word in self.themes:
                themes.extend(self.themes[word])
        
        # Убираем дубликаты
        all_words = list(set(main_words + synonyms + themes))
        
        logger.info(f"Query expansion: '{query}' -> main: {main_words}, synonyms: {synonyms}, themes: {themes}")
        
        return all_words, main_words

class BM25Scorer:
    """BM25 скоринг"""
    
    def __init__(self, k1: float = 1.2, b: float = 0.75):
        self.k1 = k1
        self.b = b
        self.doc_freqs = {}
        self.idf = {}
        self.doc_len = {}
        self.avgdl = 0.0
        self.corpus_size = 0
    
    def fit(self, documents: List[str]):
        """Обучение на корпусе документов"""
        self.corpus_size = len(documents)
        self.doc_freqs = defaultdict(int)
        self.doc_len = {}
        
        # Считаем частоты терминов и длины документов
        for i, doc in enumerate(documents):
            words = doc.split()
            self.doc_len[i] = len(words)
            
            for word in set(words):  # Уникальные слова в документе
                self.doc_freqs[word] += 1
        
        # Средняя длина документа
        self.avgdl = sum(self.doc_len.values()) / self.corpus_size
        
        # IDF для каждого термина
        for word, freq in self.doc_freqs.items():
            self.idf[word] = math.log((self.corpus_size - freq + 0.5) / (freq + 0.5))
    
    def score(self, query: List[str], doc_id: int, doc_words: List[str]) -> float:
        """Вычисление BM25 скора"""
        score = 0.0
        doc_len = self.doc_len[doc_id]
        
        for word in query:
            if word in self.idf:
                tf = doc_words.count(word)
                score += self.idf[word] * (tf * (self.k1 + 1)) / (
                    tf + self.k1 * (1 - self.b + self.b * doc_len / self.avgdl)
                )
        
        return score

class NGramScorer:
    """N-gram скоринг для fuzzy поиска"""
    
    def __init__(self, n_values: List[int] = [3, 4, 5]):
        self.n_values = n_values
        self.weights = {3: 0.6, 4: 0.3, 5: 0.1}  # Веса для разных n
    
    def get_ngrams(self, text: str, n: int) -> Set[str]:
        """Получение n-грамм"""
        if len(text) < n:
            return {text}
        return {text[i:i+n] for i in range(len(text) - n + 1)}
    
    def score(self, query: str, text: str) -> float:
        """Вычисление n-gram скора"""
        query_ngrams = set()
        text_ngrams = set()
        
        for n in self.n_values:
            query_ngrams.update(self.get_ngrams(query, n))
            text_ngrams.update(self.get_ngrams(text, n))
        
        if not query_ngrams or not text_ngrams:
            return 0.0
        
        intersection = len(query_ngrams.intersection(text_ngrams))
        union = len(query_ngrams.union(text_ngrams))
        
        jaccard = intersection / union if union > 0 else 0.0
        
        # Взвешенная сумма по n-граммам
        weighted_score = 0.0
        for n in self.n_values:
            n_query = self.get_ngrams(query, n)
            n_text = self.get_ngrams(text, n)
            n_intersection = len(n_query.intersection(n_text))
            n_union = len(n_query.union(n_text))
            n_jaccard = n_intersection / n_union if n_union > 0 else 0.0
            weighted_score += n_jaccard * self.weights[n]
        
        return weighted_score

class TFIDFScorer:
    """TF-IDF скоринг"""
    
    def __init__(self):
        self.idf = {}
        self.vocab = set()
        self.corpus_size = 0
    
    def fit(self, documents: List[str]):
        """Обучение на корпусе документов"""
        self.corpus_size = len(documents)
        doc_freqs = defaultdict(int)
        
        for doc in documents:
            words = set(doc.split())
            self.vocab.update(words)
            for word in words:
                doc_freqs[word] += 1
        
        # Вычисляем IDF
        for word in self.vocab:
            self.idf[word] = math.log(self.corpus_size / doc_freqs[word])
    
    def score(self, query: List[str], doc_words: List[str]) -> float:
        """Вычисление TF-IDF скора"""
        if not doc_words:
            return 0.0
        
        # TF для документа
        word_counts = Counter(doc_words)
        doc_len = len(doc_words)
        
        score = 0.0
        for word in query:
            if word in self.idf:
                tf = word_counts[word] / doc_len
                score += tf * self.idf[word]
        
        return score

class HybridSearchEngine:
    """Гибридный поисковый движок"""
    
    def __init__(self):
        self.query_rewriter = QueryRewriter()
        self.bm25_scorer = BM25Scorer()
        self.ngram_scorer = NGramScorer()
        self.tfidf_scorer = TFIDFScorer()
        
        # Веса компонентов
        self.weights = {
            'bm25': 0.45,
            'tfidf': 0.20,
            'ngram': 0.25,
            'semantic': 0.10  # Пока не используем
        }
        
        # Бусты
        self.boosts = {
            'theme': 0.10,
            'confession': 0.10,
            'canonical': 0.05
        }
        
        # Канонические источники
        self.canonical_sources = {
            'orthodox': ['библия', 'евангелие', 'послание', 'символ веры'],
            'sunni': ['коран', 'бухари', 'муслим', 'абу дауд'],
            'shia': ['коран', 'аль-кафи', 'бихар аль-анвар']
        }
        
        self.documents = []
        self.document_metadata = []
        self.is_fitted = False
    
    def fit(self, documents: List[str], metadata: List[Dict[str, Any]]):
        """Обучение на корпусе документов"""
        self.documents = documents
        self.document_metadata = metadata
        
        # Нормализуем документы
        normalized_docs = [self.query_rewriter.normalize_text(doc) for doc in documents]
        
        # Обучаем скореры
        self.bm25_scorer.fit(normalized_docs)
        self.tfidf_scorer.fit(normalized_docs)
        
        self.is_fitted = True
        logger.info(f"Hybrid search engine fitted on {len(documents)} documents")
    
    def search(self, query: str, confession: str = None, limit: int = 20) -> List[SearchResult]:
        """Поиск с гибридным скорингом"""
        if not self.is_fitted:
            raise ValueError("Search engine not fitted. Call fit() first.")
        
        # Этап 1: Query rewrite
        expanded_query, main_query = self.query_rewriter.expand_query(query)
        logger.info(f"Query: '{query}' -> expanded: {expanded_query}")
        
        # Этап 2: Генерация кандидатов
        candidates = self._generate_candidates(expanded_query, limit * 6)  # 120 кандидатов
        logger.info(f"Generated {len(candidates)} candidates")
        
        # Этап 3: Переоценка с бустами
        scored_results = self._rerank_candidates(candidates, expanded_query, main_query, confession)
        
        # Этап 4: Адаптивный порог
        final_results = self._apply_adaptive_threshold(scored_results, limit)
        
        # Этап 5: Анти-туннель фильтры
        final_results = self._apply_anti_tunnel_filters(final_results)
        
        logger.info(f"Final results: {len(final_results)} documents")
        return final_results
    
    def _generate_candidates(self, query: List[str], limit: int) -> List[int]:
        """Генерация кандидатов через разные методы"""
        candidates = set()
        
        # BM25 кандидаты (60)
        bm25_scores = []
        for i, doc in enumerate(self.documents):
            normalized_doc = self.query_rewriter.normalize_text(doc)
            doc_words = normalized_doc.split()
            score = self.bm25_scorer.score(query, i, doc_words)
            if score > 0:
                bm25_scores.append((i, score))
        
        bm25_scores.sort(key=lambda x: x[1], reverse=True)
        candidates.update([i for i, _ in bm25_scores[:60]])
        
        # N-gram кандидаты (40)
        ngram_scores = []
        query_text = ' '.join(query)
        for i, doc in enumerate(self.documents):
            normalized_doc = self.query_rewriter.normalize_text(doc)
            score = self.ngram_scorer.score(query_text, normalized_doc)
            if score > 0:
                ngram_scores.append((i, score))
        
        ngram_scores.sort(key=lambda x: x[1], reverse=True)
        candidates.update([i for i, _ in ngram_scores[:40]])
        
        # TF-IDF кандидаты (20)
        tfidf_scores = []
        for i, doc in enumerate(self.documents):
            normalized_doc = self.query_rewriter.normalize_text(doc)
            doc_words = normalized_doc.split()
            score = self.tfidf_scorer.score(query, doc_words)
            if score > 0:
                tfidf_scores.append((i, score))
        
        tfidf_scores.sort(key=lambda x: x[1], reverse=True)
        candidates.update([i for i, _ in tfidf_scores[:20]])
        
        return list(candidates)[:limit]
    
    def _rerank_candidates(self, candidates: List[int], expanded_query: List[str], 
                          main_query: List[str], confession: str) -> List[SearchResult]:
        """Переоценка кандидатов с бустами"""
        results = []
        
        for doc_id in candidates:
            doc = self.documents[doc_id]
            metadata = self.document_metadata[doc_id]
            normalized_doc = self.query_rewriter.normalize_text(doc)
            doc_words = normalized_doc.split()
            
            # Базовые скореры
            bm25_score = self.bm25_scorer.score(expanded_query, doc_id, doc_words)
            tfidf_score = self.tfidf_scorer.score(expanded_query, doc_words)
            ngram_score = self.ngram_scorer.score(' '.join(expanded_query), normalized_doc)
            
            # Базовый скор
            base_score = (
                bm25_score * self.weights['bm25'] +
                tfidf_score * self.weights['tfidf'] +
                ngram_score * self.weights['ngram']
            )
            
            # Бусты
            boosts_applied = []
            total_boost = 0.0
            
            # Тематический буст
            theme_boost = self._calculate_theme_boost(expanded_query, metadata)
            if theme_boost > 0:
                total_boost += theme_boost
                boosts_applied.append('theme')
            
            # Конфессиональный буст
            confession_boost = self._calculate_confession_boost(confession, metadata)
            if confession_boost > 0:
                total_boost += confession_boost
                boosts_applied.append('confession')
            
            # Канонический буст
            canonical_boost = self._calculate_canonical_boost(metadata)
            if canonical_boost > 0:
                total_boost += canonical_boost
                boosts_applied.append('canonical')
            
            final_score = base_score + total_boost
            
            result = SearchResult(
                id=doc_id,
                text=doc,
                book_name=metadata.get('book_name', ''),
                author=metadata.get('author', ''),
                confession=metadata.get('confession', ''),
                theme=metadata.get('theme', ''),
                score=final_score,
                score_breakdown={
                    'bm25': bm25_score,
                    'tfidf': tfidf_score,
                    'ngram': ngram_score,
                    'boosts': total_boost
                },
                boosts_applied=boosts_applied
            )
            results.append(result)
        
        return results
    
    def _calculate_theme_boost(self, query: List[str], metadata: Dict[str, Any]) -> float:
        """Вычисление тематического буста"""
        theme = metadata.get('theme', '').lower()
        if not theme:
            return 0.0
        
        theme_words = theme.split()
        matches = sum(1 for word in query if word in theme_words)
        
        if matches > 0:
            return min(self.boosts['theme'], matches * 0.03)
        return 0.0
    
    def _calculate_confession_boost(self, confession: str, metadata: Dict[str, Any]) -> float:
        """Вычисление конфессионального буста"""
        if not confession:
            return 0.0
        
        doc_confession = metadata.get('confession', '').lower()
        if doc_confession == confession.lower():
            return self.boosts['confession']
        
        # Буст для общих тем
        if confession.lower() in ['orthodox', 'sunni', 'shia']:
            return self.boosts['confession'] * 0.5
        
        return 0.0
    
    def _calculate_canonical_boost(self, metadata: Dict[str, Any]) -> float:
        """Вычисление канонического буста"""
        book_name = metadata.get('book_name', '').lower()
        author = metadata.get('author', '').lower()
        
        # Проверяем канонические источники
        for confession, sources in self.canonical_sources.items():
            for source in sources:
                if source in book_name or source in author:
                    return self.boosts['canonical']
        
        return 0.0
    
    def _apply_adaptive_threshold(self, results: List[SearchResult], limit: int) -> List[SearchResult]:
        """Применение адаптивного порога"""
        if not results:
            return results
        
        # Сортируем по скору
        results.sort(key=lambda x: x.score, reverse=True)
        
        # Вычисляем статистики
        scores = [r.score for r in results]
        median_score = np.median(scores)
        p80_score = np.percentile(scores, 80)
        
        # Адаптивный порог
        threshold = max(median_score * 0.65, p80_score * 0.85)
        
        # Фильтруем по порогу
        filtered_results = [r for r in results if r.score >= threshold]
        
        # Гарантируем минимум 15 результатов
        if len(filtered_results) < 15:
            filtered_results = results[:15]
        
        # Ограничиваем максимумом
        if len(filtered_results) > limit:
            filtered_results = filtered_results[:limit]
        
        logger.info(f"Score stats: min={min(scores):.3f}, median={median_score:.3f}, "
                   f"p80={p80_score:.3f}, max={max(scores):.3f}")
        logger.info(f"Threshold: {threshold:.3f}, returned: {len(filtered_results)}")
        
        return filtered_results
    
    def _apply_anti_tunnel_filters(self, results: List[SearchResult]) -> List[SearchResult]:
        """Применение анти-туннель фильтров"""
        if not results:
            return results
        
        # Группировка: не более 3 записей из одной книги подряд
        filtered_results = []
        book_counts = defaultdict(int)
        
        for result in results:
            book_name = result.book_name
            if book_counts[book_name] < 3:
                filtered_results.append(result)
                book_counts[book_name] += 1
            else:
                # Пропускаем, но добавляем в конец если есть место
                if len(filtered_results) < 20:
                    filtered_results.append(result)
        
        # Дедупликация по похожим отрывкам (Jaccard >= 0.9)
        final_results = []
        for result in filtered_results:
            is_duplicate = False
            for existing in final_results:
                jaccard = self._calculate_jaccard_similarity(result.text, existing.text)
                if jaccard >= 0.9:
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                final_results.append(result)
        
        return final_results
    
    def _calculate_jaccard_similarity(self, text1: str, text2: str) -> float:
        """Вычисление Jaccard similarity"""
        words1 = set(self.query_rewriter.normalize_text(text1).split())
        words2 = set(self.query_rewriter.normalize_text(text2).split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))
        
        return intersection / union if union > 0 else 0.0
