from openai import AsyncOpenAI


async def generate_response(api_key: str, agent_data: dict, chat_history: list, user_message: str) -> str:
    client = AsyncOpenAI(api_key=api_key)
    
    # Build context from website and chat history
    context = f"""You are a voice agent for {agent_data['website_url']}.
Target audience: {agent_data['target_audience']}

Website content summary:
{agent_data['website_content']}

Background context:
{agent_data['assets']['background']}

Chat history:
{_format_chat_history(chat_history)}

Respond naturally as the website's voice agent. Keep responses conversational and helpful."""

    try:
        response = await client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": context},
                {"role": "user", "content": user_message}
            ],
            max_tokens=200,
            temperature=0.7
        )
        
        return response.choices[0].message.content.strip()
    except Exception as e:
        raise e


def _format_chat_history(history: list) -> str:
    if not history:
        return "No previous conversation."
    
    formatted = []
    for msg in history[-5:]:  # Last 5 messages
        role = "User" if msg["type"] == "user" else "Assistant"
        formatted.append(f"{role}: {msg['text']}")
    
    return "\n".join(formatted) 