from flask import Flask, render_template_string, request, jsonify
import requests
import os
import markdown  # For converting markdown to HTML

app = Flask(__name__)

# HTML Template with Tailwind CSS for styling
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Deepseek Chatbot</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.7.0/styles/github.min.css">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.7.0/highlight.min.js"></script>
    <script>hljs.highlightAll();</script>
    <style>
        .prose {
            max-width: 100%;
        }
        .prose ul {
            list-style-type: disc;
            padding-left: 1.5rem;
        }
        .prose ol {
            list-style-type: decimal;
            padding-left: 1.5rem;
        }
        .prose pre {
            background-color: #f6f8fa;
            padding: 1rem;
            border-radius: 0.5rem;
            overflow-x: auto;
        }
        .prose code {
            background-color: #f6f8fa;
            padding: 0.2rem 0.4rem;
            border-radius: 0.2rem;
            font-family: monospace;
        }
    </style>
</head>
<body class="bg-gray-100">
    <div class="container mx-auto max-w-3xl p-4">
        <h1 class="text-3xl font-bold text-center my-6 text-blue-600">Deepseek Chatbot</h1>
        
        <div id="chat-container" class="bg-white rounded-lg shadow-md p-4 mb-4 h-96 overflow-y-auto">
            {% for message in conversation %}
                {% if message.role == 'user' %}
                    <div class="flex justify-end mb-4">
                        <div class="bg-blue-500 text-white rounded-lg py-2 px-4 max-w-xs md:max-w-md lg:max-w-lg">
                            {{ message.content }}
                        </div>
                    </div>
                {% else %}
                    <div class="flex justify-start mb-4">
                        <div class="bg-gray-200 text-gray-800 rounded-lg py-2 px-4 max-w-xs md:max-w-md lg:max-w-lg prose">
                            {{ message.content|safe }}
                        </div>
                    </div>
                {% endif %}
            {% endfor %}
        </div>
        
        <form id="chat-form" class="flex gap-2">
            <input type="text" id="user-input" 
                   class="flex-1 border border-gray-300 rounded-lg py-2 px-4 focus:outline-none focus:ring-2 focus:ring-blue-500"
                   placeholder="Type your message here..." autocomplete="off">
            <button type="submit" 
                    class="bg-blue-500 hover:bg-blue-600 text-white font-bold py-2 px-6 rounded-lg transition">
                Send
            </button>
        </form>
    </div>

    <script>
        document.getElementById('chat-form').addEventListener('submit', async function(e) {
            e.preventDefault();
            const input = document.getElementById('user-input');
            const message = input.value.trim();
            if (!message) return;
            
            // Add user message to chat
            const chatContainer = document.getElementById('chat-container');
            chatContainer.innerHTML += `
                <div class="flex justify-end mb-4">
                    <div class="bg-blue-500 text-white rounded-lg py-2 px-4 max-w-xs md:max-w-md lg:max-w-lg">
                        ${message}
                    </div>
                </div>
            `;
            
            input.value = '';
            chatContainer.scrollTop = chatContainer.scrollHeight;
            
            // Get assistant response
            const response = await fetch('/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ message: message })
            });
            
            const data = await response.json();
            if (data.response) {
                chatContainer.innerHTML += `
                    <div class="flex justify-start mb-4">
                        <div class="bg-gray-200 text-gray-800 rounded-lg py-2 px-4 max-w-xs md:max-w-md lg:max-w-lg prose">
                            ${data.response}
                        </div>
                    </div>
                `;
                chatContainer.scrollTop = chatContainer.scrollHeight;
                hljs.highlightAll();
            }
        });
    </script>
</body>
</html>
"""

@app.route('/', methods=['GET'])
def home():
    return render_template_string(HTML_TEMPLATE, conversation=[])

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get('message')
    if not user_message:
        return jsonify({'error': 'No message provided'}), 400
    
    # Call Deepseek API (replace with your actual API call)
    headers = {
        "Authorization": f"Bearer {os.getenv('DEEPSEEK_API_KEY')}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": user_message}],
        "temperature": 0.7,
        "max_tokens": 1000
    }
    
    try:
        response = requests.post("https://api.deepseek.com/v1/chat/completions", 
                               headers=headers, 
                               json=payload)
        response.raise_for_status()
        data = response.json()
        assistant_message = data['choices'][0]['message']['content']
        
        # Convert markdown to HTML
        html_content = markdown.markdown(assistant_message, extensions=['fenced_code', 'tables'])
        
        return jsonify({'response': html_content})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)