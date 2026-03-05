import json
from collections.abc import AsyncGenerator
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.repositories.audit_repo import AuditRepository
from app.schemas.audit_log import AuditLogOut


class AuditService:
    def __init__(self, db: AsyncSession):
        self.audit_repo = AuditRepository(db)

    async def list_logs(
        self, org_id: UUID, limit: int = 20, offset: int = 0
    ) -> list[AuditLogOut]:
        logs = await self.audit_repo.list_by_org(org_id, limit, offset)
        return [AuditLogOut.model_validate(log) for log in logs]

    async def ask_chatbot(self, org_id: UUID, question: str, stream: bool = False):
        logs = await self.audit_repo.get_today_logs(org_id)
        logs_text = "\n".join(
            f"- [{log.created_at.isoformat()}] user={log.user_id} action={log.action} metadata={json.dumps(log.metadata_)}"
            for log in logs
        )

        system_prompt = (
            "You are an AI assistant that analyzes organization audit logs. "
            "Answer the user's question based ONLY on the audit log data provided below.\n\n"
            f"Today's audit logs:\n{logs_text}\n\n"
            "If there are no logs, say so. Be concise and accurate."
        )

        if stream:
            return self._stream_response(system_prompt, question)
        else:
            return await self._get_response(system_prompt, question)

    async def _get_response(self, system_prompt: str, question: str) -> str:
        provider = settings.LLM_PROVIDER.lower()

        if provider == "openai":
            return await self._openai_response(system_prompt, question)
        elif provider == "gemini":
            return await self._gemini_response(system_prompt, question)
        elif provider == "claude":
            return await self._claude_response(system_prompt, question)
        else:
            return f"Unsupported LLM provider: {provider}"

    async def _stream_response(
        self, system_prompt: str, question: str
    ) -> AsyncGenerator[str, None]:
        provider = settings.LLM_PROVIDER.lower()

        if provider == "openai":
            async for chunk in self._openai_stream(system_prompt, question):
                yield chunk
        elif provider == "gemini":
            async for chunk in self._gemini_stream(system_prompt, question):
                yield chunk
        elif provider == "claude":
            async for chunk in self._claude_stream(system_prompt, question):
                yield chunk
        else:
            yield f"Unsupported LLM provider: {provider}"

    # --- OpenAI ---

    async def _openai_response(self, system_prompt: str, question: str) -> str:
        from openai import AsyncOpenAI

        client = AsyncOpenAI(api_key=settings.LLM_API_KEY)
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": question},
            ],
        )
        return response.choices[0].message.content or ""

    async def _openai_stream(
        self, system_prompt: str, question: str
    ) -> AsyncGenerator[str, None]:
        from openai import AsyncOpenAI

        client = AsyncOpenAI(api_key=settings.LLM_API_KEY)
        stream = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": question},
            ],
            stream=True,
        )
        async for chunk in stream:
            delta = chunk.choices[0].delta.content
            if delta:
                yield f"data: {delta}\n\n"

    # --- Gemini ---

    async def _gemini_response(self, system_prompt: str, question: str) -> str:
        import google.generativeai as genai

        genai.configure(api_key=settings.LLM_API_KEY)
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(f"{system_prompt}\n\nUser question: {question}")
        return response.text

    async def _gemini_stream(
        self, system_prompt: str, question: str
    ) -> AsyncGenerator[str, None]:
        import google.generativeai as genai

        genai.configure(api_key=settings.LLM_API_KEY)
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(
            f"{system_prompt}\n\nUser question: {question}",
            stream=True,
        )
        for chunk in response:
            if chunk.text:
                yield f"data: {chunk.text}\n\n"

    # --- Claude ---

    async def _claude_response(self, system_prompt: str, question: str) -> str:
        from anthropic import AsyncAnthropic

        client = AsyncAnthropic(api_key=settings.LLM_API_KEY)
        response = await client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1024,
            system=system_prompt,
            messages=[{"role": "user", "content": question}],
        )
        return response.content[0].text

    async def _claude_stream(
        self, system_prompt: str, question: str
    ) -> AsyncGenerator[str, None]:
        from anthropic import AsyncAnthropic

        client = AsyncAnthropic(api_key=settings.LLM_API_KEY)
        async with client.messages.stream(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1024,
            system=system_prompt,
            messages=[{"role": "user", "content": question}],
        ) as stream:
            async for text in stream.text_stream:
                yield f"data: {text}\n\n"
