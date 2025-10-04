import React, { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import './ClientPage.css';

function ClientPage() {
  const { clientId } = useParams();
  const navigate = useNavigate();
  const [client, setClient] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [widgetLoaded, setWidgetLoaded] = useState(false);
  const widgetContainerRef = useRef(null);

  const handleVoiceCall = () => {
    // Try to trigger the ElevenLabs widget if it exists
    const widget = document.querySelector('elevenlabs-convai');
    const button = widget.querySelector('button');
      if (button) {
        button.click();
    }
  };

  useEffect(() => {
    fetchClient();
  }, [clientId]);

  useEffect(() => {
    // Load ElevenLabs script if not already loaded
    if (!document.querySelector('script[src*="elevenlabs"]')) {
      const script = document.createElement('script');
      script.src = 'https://unpkg.com/@elevenlabs/convai-widget-embed';
      script.async = true;
      document.body.appendChild(script);
    }

    // Initialize widget when client data is available
    if (client && widgetContainerRef.current) {
      initializeWidget();
    }
  }, [client]);

  const fetchClient = async () => {
    try {
      setLoading(true);
      const response = await fetch(`/api/client/${clientId}`);
      
      if (!response.ok) {
        throw new Error('Client not found');
      }
      
      const data = await response.json();
      setClient(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const generateMainPrompt = (assets) => {
    const now = new Date();
    const daysOfWeek = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"];
    const nytd = now.toLocaleString("en-US", { timeZone: "America/New_York", weekday: 'long', year: 'numeric', month: 'long', day: 'numeric', hour: '2-digit', minute: '2-digit', second: '2-digit'});
    const latd = now.toLocaleString("en-US", { timeZone: "America/Los_Angeles", weekday: 'long', year: 'numeric', month: 'long', day: 'numeric', hour: '2-digit', minute: '2-digit', second: '2-digit'});
    const sytd = now.toLocaleString("en-US", { timeZone: "Australia/Sydney", weekday: 'long', year: 'numeric', month: 'long', day: 'numeric', hour: '2-digit', minute: '2-digit', second: '2-digit'});
    
    const assistantName = "Ariana";
    const languageTone = "Casual laid back Australian";
    const companyProfile = assets.background || "";
    const additionalRules = assets.rules || "";
    const scripts = assets.script || "";
    const faqs = assets.faqs || "";
    
    // Helper function to escape quotes and clean text for HTML attribute
    const escapeForAttribute = (text) => {
      if (!text) return "";
      return text
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#39;")
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/\n/g, " ")
        .replace(/\s+/g, " ")
        .trim();
    };
    
    // Create the prompt with proper escaping
    const prompt = `## CONTEXT ##

Today is ${daysOfWeek[now.getUTCDay()]}, ${now.toISOString().replace("T",", ").replace("Z"," in UTC")}
Today is ${nytd} in America/New York
Today is ${latd} in America/Los Angeles
Today is ${sytd} in Australia/Sydney

You are a human assistant named ${assistantName}, using a ${languageTone} tone, working for the company described below. Continue this conversation adhering to the below RULES, using the FAQs as reference and the script example as a guide on how to structure the call. SOUND LIKE A NORMAL HUMAN, HAVING A REAL CASUAL CONVERSATION OVER THE PHONE. Include LOTS of laid back lingo and softening and filler words like "kinda...", "really...", "uhm..." "ahhhh...", "oh yeah...".

## Our Company Introduction (Background) ##

${companyProfile}

## USER CONTEXT ##

Their Email: @UserEmail 
Their Phone: @UserPhone 

Below are additional details about the person/user you are currently speaking with. Tailor your script and replies accordingly to better match this user's needs and mindset.
@UserContext

## PRIMARY RULES TO FOLLOW - SUPERCEDES YOUR OTHER INSTRUCTIONS ##

1. Model and match the wording of the prospect you are talking with. Mirror their language, words and how they speak. Use words they say a lot. Keep your replies short if theirs are short.

2. If you have already said a phrase or sentence, do not repeat it more than twice unless specifically asked to repeat. Avoid getting stuck in loops of saying the same thing over and over again on repeat more than twice. Move on to the next step instead.

3. If you are receiving VERY incomplete sentences (or sentences which don't make sense at all) which seems like the line is cutting out on a call, mention you're sorry but bear with me, as it seems like the connection is cutting out... Could you repeat?

4. Anything in the script which is between [square brackets] DO NOT directly reply with. You should instead take whatever is between the [square brackets] as notes for your own use in DECIDING what to reply with.

5. IF SOMEONE GIVES YOU AN OBJECTION OR IS NOT INTERESTED, DO NOT HANG UP IMMEDIATELY. INSTEAD, HANDLE THE OBJECTION AND CONTINUE DOWN THE SCRIPT. ONE OPTION IS TO ACKNOWLEDGE WHAT THEY SAID THEN SAY "CAN I JUST ASK A QUICK QUESTION..." AND THEN SAY THE NEXT LINE. ANOTHER OPTION IS TO REFER TO THE FAQS BELOW. DO NOT HANG UP UNTIL YOU HAVE HANDLED AT LEAST 3 OBJECTIONS.

6. IF SOMEONE ASKS A QUESTION, ANSWER IT BEFORE SAYING YOUR NEXT LINE! DON'T IGNORE THEM! ALWAYS BLEND WHAT THE PERSON SAID, INTO YOUR NEXT LINE, BEFORE YOU CONTINUE.

7. If someone is interested but wishes for you to call them back at a future date, first try keep them on the phone 1 time, if they still ask you to call them back again at a future date, then first find out which date, and say no problem you'll talk to them at the time they said to call back. BUT if they say to call back later and it DOES NOT sound like they are interested, try to keep them on the phone at least 3 times!

8. If someone wants to be removed from our list or opt out, first tell them "no problem we can do that... Just checking, you enquired about [what we're offering], right?" If they say they did, continue the conversation per the script. If they say they didn't, say something like "No problem must be the wrong number. Enjoy your day!" or a more appropriate response based on the context of the conversation.

9. Use ACTIVE LISTENING! If someone says something or asks a particular question, DO NOT simply say the next line in your script! Instead, make what you say actually MAKE SENSE in the context of the conversation! Don't talk AT them, instead, HAVE A NATURAL CONVERSATION. Repeat what they say back, answer questions, and blend their context into your next reply.

## ADDITIONAL RULES ##

${additionalRules}

## EXAMPLE SCRIPT TO LOOSELY FOLLOW FOR CALL CONVERSATIONS ##
Script outline - keep it on track and bring the conversation back to script! Use a ${languageTone} tone. DO NOT say anything in between [square brackets], these are just YOUR notes to help you DECIDE what to say next, or to tell you what to do.

NOTE: IF their first message sounds like an answering machine voice message, like "PLEASE LEAVE A MESSAGE" or "VOICE MAIL", then LEAVE A VOICE MESSAGE AND HANG UP. DO NOT CONTINUE THE SCRIPT!

${scripts}

## FAQS AND OBJECTIONS/HANDLES ##
If answering a FAQ, follow your answer up by continuing down the script. If unable to answer a question accurately, say you're unsure on the specifics, and that you can let your team know that you'd like those details.

${faqs}`;

    // Log the prompt length for debugging
    console.log('Generated prompt length:', prompt.length);
    
    // Return escaped prompt for use in HTML attribute
    return escapeForAttribute(prompt);
  };

  const initializeWidget = () => {
    if (!widgetContainerRef.current || !client) return;

    console.log('Creating widget for:', client.company_name);

    // Clear existing widget
    widgetContainerRef.current.innerHTML = '';

    // Generate main prompt using client's prompts data
    const mainPrompt = generateMainPrompt(client.prompts);
    console.log('Generated prompt:', mainPrompt);

    // Create ElevenLabs widget element with all attributes
    const widget = document.createElement('elevenlabs-convai');
    widget.setAttribute('agent-id', 'agent_7201k5s3wn87e8fbzzss122we14r');
    widget.setAttribute('override-prompt', mainPrompt);
    widget.setAttribute('override-first-message', 'Hello! How can I help you today?');
    widget.setAttribute('action-text', 'Start Voice Chat');
    
    widgetContainerRef.current.appendChild(widget);
    console.log('Widget created and appended');
  };

  if (loading) {
    return (
      <div className="client-page">
        <div className="loading-container">
          <div className="spinner"></div>
          <p>Loading client...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="client-page">
        <div className="error-container">
          <h2>Error</h2>
          <p>{error}</p>
          <button onClick={() => navigate('/')} className="back-btn">
            ← Back to Home
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="client-page">
      <button onClick={() => navigate('/')} className="back-btn">← Back to Home</button>
      <div className="client-header">
        <h1>{client?.company_name || 'Client Agent'}</h1>
        <div className="client-details">
          <p><strong>Website:</strong> <a href={client?.request?.website_url} target="_blank" rel="noopener noreferrer">{client?.request?.website_url}</a></p>
          <p><strong>Target Audience:</strong> {client?.request?.target_audience}</p>
        </div>
      </div>
      
      <div ref={widgetContainerRef}>
        {/* ElevenLabs widget will be inserted here */}
      </div>
    </div>
  );
}

export default ClientPage;

