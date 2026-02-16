// static/script.js

document.addEventListener('DOMContentLoaded', () => {
    const chatBox = document.getElementById('chat-box');
    const chatForm = document.getElementById('chat-form');
    const messageInput = document.getElementById('message-input');
    const typingIndicator = document.getElementById('typing-indicator');
    
    // --- MODIFIED: Get username from sessionStorage ---
    // This value is set by the login page.
    const userId = sessionStorage.getItem('chatbot_username');

    // If no username is found, the user hasn't logged in. Redirect them.
    if (!userId) {
        window.location.href = '/'; // Redirect to the login page
        return; // Stop executing the script
    }
    // --- END MODIFICATION ---

    // Function to add a message to the chat box
    const addMessage = (text, sender, requiresReward = false) => {
        const messageElement = document.createElement('div');
        messageElement.classList.add('message', `${sender}-message`);
        
        const textElement = document.createElement('p');
        textElement.textContent = text;
        messageElement.appendChild(textElement);

        if (sender === 'bot' && requiresReward) {
            const feedbackContainer = document.createElement('div');
            feedbackContainer.classList.add('feedback-container');

            const thumbUp = document.createElement('button');
            thumbUp.innerHTML = '👍';
            thumbUp.classList.add('feedback-btn');
            thumbUp.onclick = () => sendFeedback(1, feedbackContainer);
            
            const thumbDown = document.createElement('button');
            thumbDown.innerHTML = '👎';
            thumbDown.classList.add('feedback-btn');
            thumbDown.onclick = () => sendFeedback(-1, feedbackContainer);

            feedbackContainer.appendChild(thumbUp);
            feedbackContainer.appendChild(thumbDown);
            messageElement.appendChild(feedbackContainer);
        }

        chatBox.appendChild(messageElement);
        chatBox.scrollTop = chatBox.scrollHeight;
    };

    const showTyping = (show) => {
        typingIndicator.style.display = show ? 'block' : 'none';
        if (show) chatBox.scrollTop = chatBox.scrollHeight;
    };

    chatForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const messageText = messageInput.value.trim();
        if (!messageText) return;

        addMessage(messageText, 'user');
        messageInput.value = '';
        showTyping(true);

        try {
            // --- MODIFIED: Updated API endpoint ---
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    user_id: userId,
                    message: messageText,
                }),
            });

            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            
            const data = await response.json();
            showTyping(false);
            addMessage(data.response, 'bot', data.requires_reward);

        } catch (error) {
            showTyping(false);
            addMessage('Oops! Something went wrong. Please try again.', 'bot');
            console.error('Fetch error:', error);
        }
    });

    const sendFeedback = async (reward, container) => {
        container.querySelectorAll('.feedback-btn').forEach(btn => {
            btn.classList.add('disabled');
            btn.onclick = null;
        });
        
        try {
            // --- MODIFIED: Updated API endpoint ---
            await fetch('/api/feedback', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    user_id: userId,
                    reward: reward,
                }),
            });
            
            const confirmation = document.createElement('span');
            confirmation.textContent = ' Thanks!';
            confirmation.style.fontSize = '0.8em';
            confirmation.style.opacity = '0.7';
            container.appendChild(confirmation);

        } catch (error) {
            console.error('Feedback error:', error);
        }
    };

    // Initial greeting from the bot, now personalized
    addMessage(`Hello ${userId}! I'm Davila. How can I assist you today?`, 'bot');
});