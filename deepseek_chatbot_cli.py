import os
import requests
from colorama import init, Fore, Style

class DeepseekCLIChatbot:
    def __init__(self, api_key):
        self.api_key = api_key
        self.api_url = "https://api.deepseek.com/v1/chat/completions"  # Verify correct endpoint
        self.conversation_history = []
        init()  # Initialize colorama for Windows ANSI color support
        
    def chat(self):
        print(f"\n{Fore.CYAN}Deepseek CLI Chatbot (type 'quit' to exit){Style.RESET_ALL}\n")
        print(f"{Fore.GREEN}Hello! How can I assist you today?{Style.RESET_ALL}")
        
        while True:
            try:
                user_input = input(f"\n{Fore.YELLOW}You:{Style.RESET_ALL} ")
                
                if user_input.lower() in ['quit', 'exit']:
                    print(f"{Fore.CYAN}Goodbye!{Style.RESET_ALL}")
                    break
                if not user_input.strip():
                    continue
                
                # Add user message to conversation history
                self.conversation_history.append({"role": "user", "content": user_input})
                
                # Call Deepseek API
                response = self._call_deepseek_api()
                
                # Process and display response
                if response:
                    assistant_message = response
                    print(f"\n{Fore.BLUE}Assistant:{Style.RESET_ALL} {assistant_message}")
                    self.conversation_history.append({"role": "assistant", "content": assistant_message})
                
            except KeyboardInterrupt:
                print(f"\n{Fore.CYAN}Goodbye!{Style.RESET_ALL}")
                break
            except Exception as e:
                print(f"\n{Fore.RED}Error:{Style.RESET_ALL} {str(e)}")
    
    def _call_deepseek_api(self):
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "deepseek-chat",  # Verify the correct model name
            "messages": self.conversation_history,
            "temperature": 0.7,
            "max_tokens": 1000
        }
        
        try:
            response = requests.post(self.api_url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
            return data['choices'][0]['message']['content']
        except requests.exceptions.RequestException as e:
            print(f"{Fore.RED}API request failed:{Style.RESET_ALL} {str(e)}")
            return None

if __name__ == "__main__":
    api_key = os.getenv("DEEPSEEK_API_KEY") or input("Enter your Deepseek API key: ")
    chatbot = DeepseekCLIChatbot(api_key)
    chatbot.chat()