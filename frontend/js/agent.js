const ELEVENLABS_AGENT_ID = "EJZVe9JVWQw5gPQiCM74";

// Wait for DOM to load
document.addEventListener('DOMContentLoaded', function() {  
    const urlParams = new URLSearchParams(window.location.search);
    const clientId = urlParams.get('client_id');
    
    if (clientId) {
        loadClientAndCreateWidget(clientId);
    }
});

// Create agent and automatically connect
async function createAgent() {
    // Get DOM elements with null checks
    const websiteUrlEl = document.getElementById("websiteUrl");
    const targetAudienceEl = document.getElementById("targetAudience");
    const createBtnEl = document.getElementById("createAgentBtn");
    const loadingSpinnerEl = document.getElementById("loadingSpinner");
    const agentStatusEl = document.getElementById("agentStatus");
    
    // Check if elements exist
    if (!websiteUrlEl || !targetAudienceEl) {
        console.error("Required form elements not found");
        return;
    }
    
    const websiteUrl = websiteUrlEl.value.trim();
    const targetAudience = targetAudienceEl.value.trim();
    
    if (!websiteUrl || !targetAudience) {
        showStatus("Please fill in all fields", "error");
        return;
    }

    // Show loading state
    if (createBtnEl) {
        createBtnEl.disabled = true;
        createBtnEl.textContent = "Creating Agent...";
    }
    if (loadingSpinnerEl) {
        loadingSpinnerEl.style.display = "block";
    }
    showStatus("Scraping website and creating agent... This may take a moment.", "loading");

    try {
        // Check for client_id in URL parameters
        const urlParams = new URLSearchParams(window.location.search);
        const clientId = urlParams.get('client_id');
        
        // Build API URL with optional client_id query parameter
        let apiUrl = "http://localhost:8000/create-voice-agent";
        if (clientId) {
            apiUrl += `?client_id=${encodeURIComponent(clientId)}`;
        }
        
        const response = await fetch(apiUrl, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                website_url: websiteUrl,
                target_audience: targetAudience
            })
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();

        // Show success
        showStatus("Agent created successfully! You can now chat.", "success");
        
        // Hide the agent creation form
        const agentCreationContainer = document.getElementById("agentCreationContainer");
        if (agentCreationContainer) {
            agentCreationContainer.style.display = "none";
        }
        
        // Create Eleven Labs widget
        createElevenLabsWidget(data.assets);
        
    } catch (error) {
        console.error("Error creating agent:", error);
        showStatus("Error creating agent: " + error.message, "error");
    } finally {
        // Reset button state
        if (createBtnEl) {
            createBtnEl.disabled = false;
            createBtnEl.textContent = "Create Voice Agent";
        }
        if (loadingSpinnerEl) {
            loadingSpinnerEl.style.display = "none";
        }
    }
}

// Load client data by ID and create Eleven Labs widget
async function loadClientAndCreateWidget(clientId) {
    try {
        showStatus("Loading client data...", "loading");
        
        const response = await fetch(`http://localhost:8000/client/${clientId}`);
        
        if (!response.ok) {
            throw new Error(`Client not found: ${response.status}`);
        }
        
        const clientData = await response.json();
        
        // Hide the agent creation form since we're loading from client data
        const agentCreationContainer = document.getElementById("agentCreationContainer");
        if (agentCreationContainer) {
            agentCreationContainer.style.display = "none";
        }
        
        // Create Eleven Labs widget with client's prompts data
        createElevenLabsWidgetFromClient(clientData);
        
        showStatus(`Client loaded successfully! Voice agent ready for ${clientData.request.website_url}`, "success");
        
    } catch (error) {
        console.error("Error loading client:", error);
        showStatus("Error loading client: " + error.message, "error");
    }
}

// Create Eleven Labs widget from client data
function createElevenLabsWidgetFromClient(clientData) {
    const widgetContainerEl = document.getElementById("elevenLabsWidget");
    const voiceContainerEl = document.getElementById("voiceWidgetContainer");
    
    if (!widgetContainerEl || !voiceContainerEl) return;
    
    // Generate main prompt using client's prompts data
    const mainPrompt = generateMainPrompt(clientData.prompts);
    console.log(mainPrompt);
    
    // Create widget HTML with client's data
    widgetContainerEl.innerHTML = `
        <h2>${clientData.company_name || 'Voice Agent'}</h2>
        <elevenlabs-convai 
            agent-id="${ELEVENLABS_AGENT_ID}"
            override-prompt="${mainPrompt}"
            override-first-message="Hello! How can I help you today?"
            action-text="Start Voice Chat">
        </elevenlabs-convai>
    `;
    console.log(widgetContainerEl.innerHTML);
    
    voiceContainerEl.style.display = "block";
}

// Create ElevenLabs widget for new agents
function createElevenLabsWidget(assets) {
    const widgetContainerEl = document.getElementById("elevenLabsWidget");
    const voiceContainerEl = document.getElementById("voiceWidgetContainer");
    
    if (!widgetContainerEl || !voiceContainerEl) return;
    
    // Generate main prompt using assets
    const mainPrompt = generateMainPrompt(assets);
    
    // Create widget HTML
    widgetContainerEl.innerHTML = `
        <elevenlabs-convai 
            agent-id="${ELEVENLABS_AGENT_ID}"
            override-prompt="${mainPrompt}"
            override-first-message="Hello! How can I help you today?"
            action-text="Start Voice Chat">
        </elevenlabs-convai>
    `;
    console.log(widgetContainerEl.innerHTML);
    
    voiceContainerEl.style.display = "block";
}
function generateMainPrompt(assets) {
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
    function escapeForAttribute(text) {
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
    }
    
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
}

// Show status messages
function showStatus(message, type) {
    const statusEl = document.getElementById("agentStatus");
    if (!statusEl) return;
    
    statusEl.textContent = message;
    statusEl.className = `status-${type}`;
}

// Reset to create new agent
function createNewAgent() {
    // Show creation form, hide chat
    const voiceContainer = document.getElementById("voiceWidgetContainer");
    
    if (voiceContainer) voiceContainer.style.display = "block";
    if (voiceContainer) voiceContainer.style.display = "none";
    
    // Reset form
    const websiteUrlEl = document.getElementById("websiteUrl");
    const targetAudienceEl = document.getElementById("targetAudience");
    
    if (websiteUrlEl) websiteUrlEl.value = "";
    if (targetAudienceEl) targetAudienceEl.value = "";
    
    showStatus("Ready to create agent", "");
}
