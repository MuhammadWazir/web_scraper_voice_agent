let ws = null;
let currentSessionId = null;

// Your ElevenLabs Agent ID - set this once here
const ELEVENLABS_AGENT_ID = "agent_7201k5s3wn87e8fbzzss122we14r"; // Replace with your actual agent ID

// Wait for DOM to load
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM loaded, agent.js ready');
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
        const response = await fetch("http://localhost:8000/create-voice-agent", {
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
        currentSessionId = data.session_id;

        // Show success
        showStatus("Agent created successfully! You can now chat.", "success");
        
        // Show chat interface and hide creation form
        const agentCreationContainer = document.getElementById("agentCreationContainer");
        const chatSection = document.getElementById("chatSection");
        
        if (agentCreationContainer) agentCreationContainer.style.display = "none";
        if (chatSection) chatSection.style.display = "block";
        
        // Auto-connect to WebSocket
        connectWebSocket();
        
        // Create ElevenLabs widget
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

// Auto-connect WebSocket after agent creation
function connectWebSocket() {
    if (!currentSessionId) return;

    const statusEl = document.getElementById("status");

    ws = new WebSocket(`ws://localhost:8000/chat/${currentSessionId}`);
    
    ws.onopen = function() {
        if (statusEl) {
            statusEl.textContent = "Connected - Ready to chat!";
            statusEl.style.color = "green";
        }
        console.log("WebSocket connected");
    };

    ws.onmessage = function(event) {
        const data = JSON.parse(event.data);
        if (data.type === "agent_ready") {
            addMessage("Agent", data.message);
        } else if (data.type === "agent_response") {
            addMessage("Agent", data.text);
        }
    };

    ws.onclose = function() {
        if (statusEl) {
            statusEl.textContent = "Disconnected";
            statusEl.style.color = "red";
        }
        console.log("WebSocket disconnected");
    };

    ws.onerror = function(error) {
        if (statusEl) {
            statusEl.textContent = "Connection error";
            statusEl.style.color = "red";
        }
        console.error("WebSocket error:", error);
    };
}

// Send message function
function sendMessage() {
    const messageInputEl = document.getElementById("messageInput");
    if (!messageInputEl) return;
    
    const message = messageInputEl.value.trim();
    
    if (!message) return;
    
    if (!ws || ws.readyState !== WebSocket.OPEN) {
        addMessage("System", "Not connected to agent. Please create an agent first.");
        return;
    }

    ws.send(JSON.stringify({
        type: "user_message",
        text: message
    }));
    
    addMessage("You", message);
    messageInputEl.value = "";
}

// Add message to chat
function addMessage(sender, text) {
    const chatEl = document.getElementById("chat");
    if (!chatEl) return;
    
    const messageDiv = document.createElement("div");
    messageDiv.className = `message ${sender === "You" ? "user" : "agent"}`;
    messageDiv.innerHTML = `<strong>${sender}:</strong> ${text}`;
    chatEl.appendChild(messageDiv);
    chatEl.scrollTop = chatEl.scrollHeight;
}

// Handle Enter key press
function handleKeyPress(event) {
    if (event.key === "Enter") {
        sendMessage();
    }
}

// Create ElevenLabs widget dynamically
function createElevenLabsWidget(agentData) {
    const widgetContainerEl = document.getElementById("elevenLabsWidget");
    const voiceContainerEl = document.getElementById("voiceWidgetContainer");
    
    if (!widgetContainerEl || !voiceContainerEl) return;
    
    // Create widget HTML
    widgetContainerEl.innerHTML = `
        <elevenlabs-convai 
            agent-id="agent_7201k5s3wn87e8fbzzss122we14r"
            override-prompt="Assist users with any questions."
            override-first-message="Hello! I am your AI assistant for this website. I have analyzed the content and can help answer questions about it. How can I assist you?"
            action-text="Start Voice Chat">
        </elevenlabs-convai>
    `;
    
    voiceContainerEl.style.display = "block";
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
    // Close existing WebSocket
    if (ws) {
        ws.close();
        ws = null;
    }
    
    currentSessionId = null;
    
    // Show creation form, hide chat
    const agentCreationContainer = document.getElementById("agentCreationContainer");
    const chatSection = document.getElementById("chatSection");
    const voiceContainer = document.getElementById("voiceWidgetContainer");
    const chatEl = document.getElementById("chat");
    
    if (agentCreationContainer) agentCreationContainer.style.display = "block";
    if (chatSection) chatSection.style.display = "none";
    if (voiceContainer) voiceContainer.style.display = "none";
    if (chatEl) chatEl.innerHTML = "";
    
    // Reset form
    const websiteUrlEl = document.getElementById("websiteUrl");
    const targetAudienceEl = document.getElementById("targetAudience");
    
    if (websiteUrlEl) websiteUrlEl.value = "";
    if (targetAudienceEl) targetAudienceEl.value = "";
    
    showStatus("Ready to create agent", "");
}
