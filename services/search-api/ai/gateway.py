"""
Provider-Agnostic Grounded AI Inference Gateway for ঞ (Nya) Search.
Supports Google Gemini, OpenAI, Ollama, and Deterministic Mock Fallback.
Adheres strictly to evidence grounding, citation verification, prompt defense,
hard budget enforcement, correlation tracking, and safe error diagnostics.
"""

import time
import httpx
import uuid
import logging
from typing import List, Dict, Any, Optional, Tuple
from config import settings
from packages.contracts.schema import AIAnswer, AIAnswerStatus, CitationItem
from ai.prompt_defense import PromptDefender
from ai.citations import CitationValidator
from ai.cost_guard import CostGuard
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger("nya.ai")


class AIGateway:
    # Model fallback cascade for Google Gemini in order of preference
    GEMINI_FALLBACK_MODELS = [
        "gemini-flash-lite-latest",
        "gemini-3.5-flash-lite",
        "gemini-flash-latest",
    ]

    def __init__(self):
        self.defender = PromptDefender()
        self.citation_validator = CitationValidator()
        self.cost_guard = CostGuard()

    async def generate_grounded_answer(
        self,
        query: str,
        retrieved_documents: List[Dict[str, Any]],
        session: AsyncSession,
        language: str = "as",
        request_id: Optional[str] = None,
    ) -> AIAnswer:
        """
        Generate grounded answer strictly backed by retrieved documents.
        Provides correlation ID, stage tracking, and typed diagnostic status.
        """
        start_time = time.time()
        req_id = request_id or f"nya-{uuid.uuid4().hex[:8]}"

        # Pipeline Stage 1: Evidence Availability Check
        if not retrieved_documents:
            logger.info(f"[{req_id}] Stage 1: No eligible evidence documents for query.")
            return AIAnswer(
                answer=(
                    "পৰ্যাপ্ত তথ্য পোৱা নগ'ল। (Insufficient evidence found in indexed sources to formulate a factual answer.)"
                    if language.startswith("as")
                    else "Insufficient evidence found in retrieved sources to formulate a factual answer."
                ),
                status=AIAnswerStatus.INSUFFICIENT_EVIDENCE,
                citations=[],
                latency_ms=round((time.time() - start_time) * 1000, 2),
                confidence=0.0,
                disclaimer="উত্তৰ প্ৰস্তুত কৰিবলৈ পৰ্যাপ্ত নিৰ্ভৰযোগ্য তথ্য উপলব্ধ নহয়।",
                request_id=req_id,
            )

        # Pipeline Stage 2: Configuration Check
        provider = settings.AI_PROVIDER.lower()
        if provider in ("gemini", "openai") and not settings.AI_API_KEY:
            logger.error(f"[{req_id}] Stage 2: Missing API key for configured provider '{provider}'.")
            return AIAnswer(
                answer=(
                    "AI সেৱা সংৰূপিত নহয়। অনুগ্ৰহ কৰি তলৰ ৱেব ফলাফল চাওক। (AI inference key is not configured.)"
                    if language.startswith("as")
                    else "AI inference service is not configured with valid credentials. Please refer to web results below."
                ),
                status=AIAnswerStatus.CONFIGURATION_ERROR,
                error_code="MISSING_API_KEY",
                citations=[],
                latency_ms=round((time.time() - start_time) * 1000, 2),
                confidence=0.0,
                disclaimer="Provider credentials not configured in environment.",
                request_id=req_id,
            )

        # Pipeline Stage 3: Cost Guard Budget Enforcement
        can_run, remaining_usd = await self.cost_guard.can_execute(session)
        if not can_run:
            logger.warning(f"[{req_id}] Stage 3: Monthly budget exceeded (remaining: ${remaining_usd:.4f}).")
            return AIAnswer(
                answer=(
                    "প্ৰস্তুত সীমা অতিক্ৰম হৈছে। (Monthly AI spending budget reached.)"
                    if language.startswith("as")
                    else "Configured monthly AI spending budget has been reached. Please refer to organic results below."
                ),
                status=AIAnswerStatus.BUDGET_EXCEEDED,
                error_code="BUDGET_EXCEEDED",
                citations=[],
                latency_ms=round((time.time() - start_time) * 1000, 2),
                confidence=0.0,
                disclaimer="Hard spending limit enforced by cost guard.",
                request_id=req_id,
            )

        # Pipeline Stage 4: Evidence Sanitization & Context Preparation
        evidence_docs = retrieved_documents[: settings.AI_MAX_EVIDENCE_DOCS]
        context_str = self.defender.build_evidence_context(evidence_docs)

        # Pipeline Stage 5: Provider Dispatch with Fault Tolerance
        raw_answer = ""
        resolved_model = settings.AI_MODEL_NAME
        cost_est = 0.0001
        tokens_est = 250
        status_flag = "success"

        try:
            if provider == "gemini":
                raw_answer, resolved_model = await self._call_gemini_with_fallback(
                    query=query,
                    context=context_str,
                    language=language,
                    req_id=req_id,
                )
            elif provider == "openai":
                raw_answer = await self._call_openai(query, context_str, language, req_id)
            elif provider == "ollama":
                raw_answer = await self._call_ollama(query, context_str, language, req_id)
            else:
                # Mock / Offline deterministic fallback mode
                raw_answer = self._generate_deterministic_grounded_answer(
                    query, evidence_docs, language
                )
                resolved_model = "deterministic-offline"

        except httpx.TimeoutException as te:
            logger.error(f"[{req_id}] Stage 5: Provider timeout after {settings.AI_TIMEOUT_SECONDS}s: {te}")
            await self.cost_guard.record_usage(
                session=session, provider=provider, model=resolved_model,
                tokens_used=0, estimated_cost_usd=0.0, status="timeout"
            )
            return AIAnswer(
                answer="AI সেৱা সময়সীমা পাৰ হ'ল। অনুগ্ৰহ কৰি তলৰ ৱেব ফলাফল চাওক। (AI inference request timed out.)",
                status=AIAnswerStatus.TIMEOUT,
                error_code="TIMEOUT",
                citations=[],
                latency_ms=round((time.time() - start_time) * 1000, 2),
                confidence=0.0,
                disclaimer="Provider request timed out. Organic web results remain available.",
                request_id=req_id,
                model_name=resolved_model,
            )

        except QuotaExceededException as qe:
            logger.warning(f"[{req_id}] Stage 5: Provider quota / rate limit exhausted: {qe.sanitized_message}")
            await self.cost_guard.record_usage(
                session=session, provider=provider, model=resolved_model,
                tokens_used=0, estimated_cost_usd=0.0, status="rate_limited"
            )
            return AIAnswer(
                answer=(
                    "দৈনিক AI সীমা অতিক্ৰম হৈছে। তলৰ ৱেব ফলাফল চাওক। (AI provider quota reached for today. Organic results are fully available below.)"
                    if language.startswith("as")
                    else "AI inference provider quota reached for today. Please refer to organic results below."
                ),
                status=AIAnswerStatus.RATE_LIMITED,
                error_code="HTTP_429_QUOTA_EXCEEDED",
                retry_after_seconds=qe.retry_after_seconds,
                citations=[],
                latency_ms=round((time.time() - start_time) * 1000, 2),
                confidence=0.0,
                disclaimer="Provider request quota exhausted. Organic results remain available.",
                request_id=req_id,
                model_name=resolved_model,
            )

        except AuthenticationException as ae:
            logger.error(f"[{req_id}] Stage 5: Authentication failure: {ae.sanitized_message}")
            return AIAnswer(
                answer="AI প্ৰমাণীকৰণ ব্যৰ্থ হ'ল। (Authentication failed for AI provider key.)",
                status=AIAnswerStatus.AUTHENTICATION_FAILED,
                error_code="HTTP_401_INVALID_KEY",
                citations=[],
                latency_ms=round((time.time() - start_time) * 1000, 2),
                confidence=0.0,
                disclaimer="Invalid or expired API key. Organic search remains available.",
                request_id=req_id,
                model_name=resolved_model,
            )

        except Exception as e:
            logger.error(f"[{req_id}] Stage 5: Unhandled inference error: {e}", exc_info=True)
            await self.cost_guard.record_usage(
                session=session, provider=provider, model=resolved_model,
                tokens_used=0, estimated_cost_usd=0.0, status="error"
            )
            return AIAnswer(
                answer="AI সেৱা উপলব্ধ নহয়। অনুগ্ৰহ কৰি তলৰ ৱেব ফলাফল চাওক। (AI answer temporarily unavailable. Please refer to web results below.)",
                status=AIAnswerStatus.PROVIDER_UNAVAILABLE,
                error_code="PROVIDER_ERROR",
                citations=[],
                latency_ms=round((time.time() - start_time) * 1000, 2),
                confidence=0.0,
                disclaimer="Inference service error. Organic results remain available.",
                request_id=req_id,
                model_name=resolved_model,
            )

        # Pipeline Stage 6: Citation Validation and Verification
        cleaned_answer, verified_citations, grounding_ratio = self.citation_validator.validate_and_link(
            raw_answer, evidence_docs
        )

        # Pipeline Stage 7: Audit Usage
        await self.cost_guard.record_usage(
            session=session,
            provider=provider,
            model=resolved_model,
            tokens_used=tokens_est,
            estimated_cost_usd=cost_est,
            status=status_flag,
        )

        latency = round((time.time() - start_time) * 1000, 2)
        logger.info(f"[{req_id}] Successfully generated grounded answer via {resolved_model} ({latency}ms, {len(verified_citations)} citations).")

        return AIAnswer(
            answer=cleaned_answer,
            status=AIAnswerStatus.GROUNDED,
            citations=verified_citations,
            latency_ms=latency,
            confidence=grounding_ratio,
            disclaimer=(
                "উত্তৰসমূহ সংগৃহীত তথ্যৰ ভিত্তিত প্ৰস্তুত কৰা হৈছে। সূত্ৰত পৰীক্ষা কৰক।"
                if language.startswith("as")
                else "AI response grounded strictly in retrieved sources. Verify with evidence below."
            ),
            model_name=resolved_model,
            request_id=req_id,
        )

    async def _call_gemini_with_fallback(
        self,
        query: str,
        context: str,
        language: str,
        req_id: str,
    ) -> Tuple[str, str]:
        """
        Calls Google Gemini with candidate model cascade fallback.
        Tries configured model first; if rate-limited (429) or not found (404),
        cascades to supported lightweight fallback models.
        """
        candidate_models = [settings.AI_MODEL_NAME] + self.GEMINI_FALLBACK_MODELS
        # Deduplicate preserving order
        models_to_try = list(dict.fromkeys(candidate_models))

        system_instruction = (
            "You are Nya (ঞ), an Assamese-first search engine answer assistant. "
            "Your task is to synthesize a clear, helpful 2-4 sentence summary strictly from the provided evidence. "
            "IMPORTANT: You MUST cite your sources using bracketed numbers [1], [2] corresponding to the evidence index "
            "immediately after each factual statement. Example: 'Kaziranga is famous for the one-horned rhinoceros [1]. It is located in Assam [2].' "
            "Do not cite numbers that do not exist in the evidence. If evidence is insufficient, state so clearly."
        )
        prompt = (
            f"{system_instruction}\n\n"
            f"EVIDENCE:\n{context}\n\n"
            f"USER QUERY: {query}\n\n"
            f"ANSWER IN THE QUERY LANGUAGE ({'Assamese' if language.startswith('as') else 'English'}) WITH [1], [2] CITATIONS:"
        )

        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.2, "maxOutputTokens": 600},
        }

        async with httpx.AsyncClient(timeout=settings.AI_TIMEOUT_SECONDS) as client:
            last_status = None
            last_err_msg = ""
            retry_seconds = None

            for m in models_to_try:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{m}:generateContent?key={settings.AI_API_KEY}"
                logger.info(f"[{req_id}] Attempting Gemini inference with model: {m}")

                try:
                    resp = await client.post(url, json=payload)
                    last_status = resp.status_code

                    if resp.status_code == 200:
                        data = resp.json()
                        candidates = data.get("candidates", [])
                        if candidates and "content" in candidates[0]:
                            parts = candidates[0]["content"].get("parts", [])
                            if parts and "text" in parts[0]:
                                logger.info(f"[{req_id}] Model {m} succeeded.")
                                return parts[0]["text"], m

                    err_json = resp.json().get("error", {}) if resp.headers.get("content-type", "").startswith("application/json") else {}
                    last_err_msg = err_json.get("message", resp.text[:200])

                    # Check for 401 / 403 Authentication failures
                    if resp.status_code in (401, 403):
                        raise AuthenticationException(sanitized_message=f"Gemini API key rejected ({resp.status_code})")

                    # Check for 429 Quota / Rate limit
                    if resp.status_code == 429:
                        logger.warning(f"[{req_id}] Model '{m}' returned 429 (Resource Exhausted). Trying fallback model in cascade...")
                        # Extract retry delay if provided by Google RPC
                        for detail in err_json.get("details", []):
                            if detail.get("@type", "").endswith("RetryInfo"):
                                raw_delay = detail.get("retryDelay", "60s").rstrip("s")
                                try:
                                    retry_seconds = int(float(raw_delay))
                                except ValueError:
                                    retry_seconds = 60
                        continue

                    # Check for 404 Model Not Found / Deprecated
                    if resp.status_code == 404:
                        logger.warning(f"[{req_id}] Model '{m}' not found or deprecated. Trying next model...")
                        continue

                except (AuthenticationException, QuotaExceededException):
                    raise
                except httpx.TimeoutException:
                    raise
                except Exception as inner_e:
                    logger.warning(f"[{req_id}] Error attempting model {m}: {inner_e}")
                    continue

            # If all models in cascade returned 429
            if last_status == 429:
                raise QuotaExceededException(
                    sanitized_message=f"Google Gemini daily free tier quota reached for all models: {last_err_msg[:120]}",
                    retry_after_seconds=retry_seconds,
                )

            raise RuntimeError(f"All Gemini models in cascade failed (Last status: {last_status}): {last_err_msg[:150]}")

    async def _call_openai(self, query: str, context: str, language: str, req_id: str) -> str:
        """Call OpenAI endpoint."""
        url = "https://api.openai.com/v1/chat/completions"
        headers = {"Authorization": f"Bearer {settings.AI_API_KEY}"}
        messages = [
            {
                "role": "system",
                "content": (
                    "You are Nya (ঞ), an Assamese-first search engine answer assistant. "
                    "Answer the user query strictly using the provided evidence. "
                    "Attach bracketed citations [1], [2] to every claim. Do not invent facts."
                ),
            },
            {
                "role": "user",
                "content": f"EVIDENCE:\n{context}\n\nQUERY: {query}",
            },
        ]
        async with httpx.AsyncClient(timeout=settings.AI_TIMEOUT_SECONDS) as client:
            resp = await client.post(
                url,
                headers=headers,
                json={"model": settings.AI_MODEL_NAME, "messages": messages, "temperature": 0.2},
            )
            if resp.status_code in (401, 403):
                raise AuthenticationException("OpenAI API key rejected")
            if resp.status_code == 429:
                raise QuotaExceededException("OpenAI rate limit / quota exceeded")
            resp.raise_for_status()
            data = resp.json()
            return data["choices"][0]["message"]["content"]

    async def _call_ollama(self, query: str, context: str, language: str, req_id: str) -> str:
        """Call local Ollama endpoint."""
        url = "http://127.0.0.1:11434/api/generate"
        prompt = f"Answer using only this evidence with citations [1], [2]:\n\n{context}\n\nQuery: {query}"
        async with httpx.AsyncClient(timeout=settings.AI_TIMEOUT_SECONDS) as client:
            resp = await client.post(url, json={"model": "llama3", "prompt": prompt, "stream": False})
            resp.raise_for_status()
            data = resp.json()
            return data.get("response", "")

    def _generate_deterministic_grounded_answer(
        self, query: str, docs: List[Dict[str, Any]], language: str
    ) -> str:
        """Deterministic grounded answer synthesizer."""
        first_doc = docs[0]
        second_doc = docs[1] if len(docs) > 1 else None

        title1 = first_doc.get("title", "")
        snip1 = first_doc.get("snippet", "")

        if language in ("as", "as_native", "as_romanized"):
            ans = f"{title1} সম্পৰ্কে উপলব্ধ তথ্য অনুসৰি: {snip1} [1]."
            if second_doc:
                title2 = second_doc.get("title", "")
                snip2 = second_doc.get("snippet", "")
                ans += f" লগতে, {title2} ত উল্লেখ থকা মতে: {snip2} [2]."
            return ans
        else:
            ans = f"According to verified records from {first_doc.get('source_name', 'sources')}: {snip1} [1]."
            if second_doc:
                ans += f" Furthermore, {second_doc.get('source_name', 'additional records')} states: {second_doc.get('snippet', '')} [2]."
            return ans


class QuotaExceededException(Exception):
    def __init__(self, sanitized_message: str, retry_after_seconds: Optional[int] = None):
        super().__init__(sanitized_message)
        self.sanitized_message = sanitized_message
        self.retry_after_seconds = retry_after_seconds


class AuthenticationException(Exception):
    def __init__(self, sanitized_message: str):
        super().__init__(sanitized_message)
        self.sanitized_message = sanitized_message
