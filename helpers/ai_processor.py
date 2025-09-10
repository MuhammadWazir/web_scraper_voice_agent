import asyncio
from openai import AsyncOpenAI
from configs.config import load_settings
from configs.constants import (
    BACKGROUND_CONTEXT_PROMPT, 
    RULES_SECTION_PROMPT,
    FAQS_SECTION_PROMPT, 
    SCRIPT_CREATION_PROMPT
)

config = load_settings()

async def process_prompts( website_url: str, content: str, audience: str, model: str = "gpt-4o"):
    print(f"Processing prompts for {website_url} and audience: {audience}")
    client = AsyncOpenAI(api_key=config.openai_api_key)
    
    prompts = {
        "background": _prepare_prompt(BACKGROUND_CONTEXT_PROMPT, website_url, content, audience),
        "rules": _prepare_prompt(RULES_SECTION_PROMPT, website_url, content, audience),
        "faqs": _prepare_prompt(FAQS_SECTION_PROMPT, website_url, content, audience),
        "script": _prepare_prompt(SCRIPT_CREATION_PROMPT, website_url, content, audience)
    }
    
    tasks = [_call_openai(client, model, prompt, key) for key, prompt in prompts.items()]
    results = await asyncio.gather(*tasks)
    
    return dict(results)


def _prepare_prompt(template: str, url: str, content: str, audience: str) -> str:
    # Common replacements
    prompt = template.replace(
        "VOICE / MESSAGING  (select one, and add the website address, which extracts it all)",
        f"VOICE - {url}"
    ).replace(
        "[user input description]",
        f"Website visitor - live chat. {audience}"
    ).replace(
        "TEXT", content
    )
    
    # Rules-specific replacements
    if "TYPE OF CONVERSATION:" in prompt:
        prompt = prompt.replace(
            "**TYPE OF CONVERSATION:",
            f"**TYPE OF CONVERSATION:\nVOICE - {url}\n\n**CONVERSATION CONTEXT:"
        )
    
    # Script-specific replacements  
    if "TYPE OF CONVERSATION RIGHT NOW:" in prompt:
        prompt = prompt.replace(
            "**TYPE OF CONVERSATION RIGHT NOW:\nVOICE / MESSAGING  (select one, and add the website address, which extracts it all)",
            f"**TYPE OF CONVERSATION RIGHT NOW:\nVOICE - {url}"
        )
    
    return prompt


async def _call_openai(client: AsyncOpenAI, model: str, prompt: str, key: str):
    system_message = "You are an expert voice agent creator. Generate the requested content based on the provided website data. Do not ask for clarification - use the context provided to create the complete output."
    
    response = await client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": prompt}
        ],
        max_tokens=2000,
        temperature=0.7
    )
    return (key, response.choices[0].message.content.strip()) 

async def create_keywords(api_key: str, website_url: str,audience: str, model: str = "gpt-4o") -> list[str]:
    print(f"Creating keywords for {website_url} and audience: {audience}")
    client = AsyncOpenAI(api_key=api_key)
    
    prompt = f"Create 10 keywords for the following website: {website_url} and audience: {audience}. Return the keywords as a comma separated values."
    
    response = await client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=50,
        temperature=0.7
    )
    keywords_list = response.choices[0].message.content.strip().split(",")
    return keywords_list

async def summarize_chunks_in_parallel(chunks: list[str], model: str = "gpt-4o") -> str:
    client = AsyncOpenAI(api_key=config.openai_api_key)
    
    async def summarize_chunk(chunk: str, index: int) -> tuple[str, str]:
        system_message = "You are an expert summarizer. Summarize the following text into a maximum of 100 words with the most important information. use the context provided to create the complete output."
        response = await client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": chunk}
            ],
            max_tokens=200,
            temperature=0.7
        )
        return (str(index), response.choices[0].message.content.strip())
    
    tasks = [summarize_chunk(chunk, i) for i, chunk in enumerate(chunks)]
    results = await asyncio.gather(*tasks)
    summaries = [result[1] for result in results]
    return "\n".join(summaries)