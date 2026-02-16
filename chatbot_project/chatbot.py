import random
import json
import os
import re
from collections import defaultdict

# --- Configuration for Learning ---
Q_TABLE_FILE = 'data/q_table.json'
USER_DATA_FILE = 'data/user_data.json'
LEARNED_KNOWLEDGE_FILE = 'data/learned_knowledge.json'

LEARNING_RATE = 0.1
DISCOUNT_FACTOR = 0.9
EXPLORATION_RATE_INITIAL = 0.2
EXPLORATION_DECAY = 0.995
MIN_EXPLORATION_RATE = 0.05
DEBUG_MODE = True

# A set of common "stop words" to ignore during keyword extraction for better matching.
STOP_WORDS = {
    'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', 'your', 'yours',
    'he', 'him', 'his', 'himself', 'she', 'her', 'hers', 'herself', 'it', 'its', 'itself',
    'they', 'them', 'their', 'theirs', 'themselves', 'what', 'which', 'who', 'whom',
    'this', 'that', 'these', 'those', 'am', 'is', 'are', 'was', 'were', 'be', 'been',
    'being', 'have', 'has', 'had', 'having', 'do', 'does', 'did', 'doing', 'a', 'an',
    'the', 'and', 'but', 'if', 'or', 'because', 'as', 'until', 'while', 'of', 'at',
    'by', 'for', 'with', 'about', 'against', 'between', 'into', 'through', 'during',
    'before', 'after', 'above', 'below', 'to', 'from', 'up', 'down', 'in', 'out', 'on',
    'off', 'over', 'under', 'again', 'further', 'then', 'once', 'here', 'there', 'when',
    'where', 'why', 'how', 'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other',
    'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too',
    'very', 's', 't', 'can', 'will', 'just', 'don', 'should', 'now', 'tell', 'me', 'about',
    'did', 'you', 'give', 'a','know'
}


# --- Chatbot Rules (Knowledge Base) ---
rules = {
    "hello": ["Hello there!", "Hi!", "Greetings! How can I help you today?"],
    "hi": ["Hello there!", "Hi!", "Greetings! How can I help you today?"],
    "how are you": ["I'm doing well, thank you!", "I'm a bot, so I don't have feelings, but I'm functioning perfectly!", "All good!", "I am great, thanks for asking!"],
    "what is your name": ["My name is Davila."],
    "my name is ": ["Nice to meet you, {name}!", "Hello, {name}!"],
    "what is my name": ["I think your name is {name}.", "Didn't you tell me your name is {name}?"],
    "help": ["How can I assist you today?", "What do you need help with?", "I'm here to help!", "I can help with common questions. What's on your mind?"],
    "bye": ["Goodbye!", "See you later!", "Farewell!", "It was nice chatting with you!"],
    "thanks": ["You're welcome!", "No problem!", "Glad to help!", "Anytime!"],
    "weather": ["I'm sorry, I don't have access to real-time weather information.", "I can't tell you the weather right now.", "I am not equipped to provide weather forecasts."],
    "time": ["I don't have a clock, but you can check your system's time!", "I am not able to tell time for you."],
    "tell me a joke": ["Why don't scientists trust atoms? Because they make up everything!", "What do you call a fake noodle? An impasta!", "Did you hear about the restaurant on the moon? Great food, no atmosphere."],
}

fallback_responses = [
    "I'm not sure I understand. Can you try rephrasing?",
    "Could you please explain that differently?",
    "I'm still learning. Can you try asking something else?",
]
rules["fallback"] = fallback_responses

class Chatbot:
    def __init__(self):
        self.q_table = defaultdict(lambda: defaultdict(float))
        self.all_users_data = {}
        self.learned_knowledge = {}
        self.exploration_rate = EXPLORATION_RATE_INITIAL
        self._load_all_data()

    # --- Data Loading and Saving ---
    def _load_json_file(self, file_path, default_value={}):
        if not os.path.exists('data'):
            os.makedirs('data')
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                try:
                    return json.load(f)
                except json.JSONDecodeError:
                    return default_value
        return default_value

    def _save_json_file(self, file_path, data):
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=4)

    def _load_all_data(self):
        # Load Q-Table
        loaded_q_data = self._load_json_file(Q_TABLE_FILE, {})
        for state, actions in loaded_q_data.items():
            for action, q_value in actions.items():
                self.q_table[state][action] = float(q_value)
        if DEBUG_MODE: print("Q-table loaded.")

        # Load other data
        self.all_users_data = self._load_json_file(USER_DATA_FILE, {})
        self.learned_knowledge = self._load_json_file(LEARNED_KNOWLEDGE_FILE, {})
        if DEBUG_MODE: print("User data and learned knowledge loaded.")

    def _save_q_table(self):
        serializable_q_table = {s: dict(a) for s, a in self.q_table.items()}
        self._save_json_file(Q_TABLE_FILE, serializable_q_table)

    def _save_user_data(self):
        self._save_json_file(USER_DATA_FILE, self.all_users_data)
        
    def _save_learned_knowledge(self):
        self._save_json_file(LEARNED_KNOWLEDGE_FILE, self.learned_knowledge)

    # --- Core Logic ---
    def _normalize_text(self, text):
        text = text.lower()
        text = re.sub(r'[^\w\s]', '', text)
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    def _extract_keywords(self, text):
        """Normalizes text and extracts keywords by removing stop words."""
        normalized_text = self._normalize_text(text)
        words = normalized_text.split()
        keywords = [word for word in words if word not in STOP_WORDS]
        return keywords

    def _find_best_match_by_keywords(self, normalized_user_input):
        """
        Finds the best matching entry from rules and learned_knowledge based on keyword overlap.
        """
        user_keywords = self._extract_keywords(normalized_user_input)
        if not user_keywords:
            return None, None, 0

        if DEBUG_MODE:
            print(f"User Keywords: {user_keywords}")

        best_match_key = None
        best_score = 0
        source = None

        search_database = {}
        search_database.update({key: 'rules' for key in rules.keys() if key != 'fallback'})
        search_database.update({key: 'learned_knowledge' for key in self.learned_knowledge.keys()})

        for key, src in search_database.items():
            key_keywords = self._extract_keywords(key)
            score = len(set(user_keywords) & set(key_keywords))
            
            if score > best_score:
                best_score = score
                best_match_key = key
                source = src
        
        if DEBUG_MODE and best_match_key:
            print(f"Found best match: '{best_match_key}' in '{source}' with score {best_score}")
            
        return best_match_key, source, best_score


    def _choose_action(self, state):
        actions_for_state = list(rules.get(state, fallback_responses))
        # Add learned knowledge responses if the state matches a learned question
        if state in self.learned_knowledge:
             actions_for_state.append(self.learned_knowledge[state])

        if not actions_for_state:
            return random.choice(fallback_responses)

        if random.uniform(0, 1) < self.exploration_rate:
            return random.choice(actions_for_state)
        else:
            available_q_values = {a: self.q_table[state][a] for a in actions_for_state if a in self.q_table[state]}
            if not available_q_values:
                return random.choice(actions_for_state)
            
            max_q_value = max(available_q_values.values())
            best_actions = [action for action, q_val in available_q_values.items() if q_val == max_q_value]
            return random.choice(best_actions)

    def _update_q_table(self, state, action, reward, next_state):
        current_q = self.q_table[state][action]
        max_next_q = 0.0
        if next_state in self.q_table and self.q_table[next_state]:
            # Consider all possible actions in the next state from rules and learned knowledge
            possible_next_actions = list(rules.get(next_state, []))
            if next_state in self.learned_knowledge:
                possible_next_actions.append(self.learned_knowledge[next_state])
            
            defined_next_actions = [a for a in possible_next_actions if a in self.q_table[next_state]]
            if defined_next_actions:
                max_next_q = max(self.q_table[next_state][a] for a in defined_next_actions)
        
        new_q = current_q + LEARNING_RATE * (reward + DISCOUNT_FACTOR * max_next_q - current_q)
        self.q_table[state][action] = new_q
        self.exploration_rate = max(MIN_EXPLORATION_RATE, self.exploration_rate * EXPLORATION_DECAY)
        self._save_q_table()


    # --- Public Methods for Application ---
    def handle_user_login(self, user_id):
        """Initializes user data if the user is new."""
        if user_id not in self.all_users_data:
            self.all_users_data[user_id] = {
                "name": None, 
                "history": [],
                "last_state": None,
                "last_action": None,
                "awaiting_answer_for": None,
                "pending_question_to_learn": None # NEW: State to hold question before confirmation
            }
            self._save_user_data()
            return f"Welcome, new user '{user_id}'!"
        return f"Welcome back, {self.all_users_data[user_id].get('name', user_id)}!"

    def get_response(self, user_id, user_input):
        """Main function to get a response from the chatbot."""
        user_data = self.all_users_data.get(user_id)
        if not user_data:
            return {"response": "Error: User not found. Please login first.", "state": "error", "requires_reward": False}

        normalized_input = self._normalize_text(user_input)
        bot_response = None
        current_state = None

        # --- Active Learning State Machine ---
        # State 1: User is providing the final answer to a question.
        if user_data.get("awaiting_answer_for"):
            question_to_learn = user_data["awaiting_answer_for"]
            # Store the normalized question and the raw answer
            self.learned_knowledge[self._normalize_text(question_to_learn)] = user_input
            bot_response = "Thanks! I've learned something new."
            
            user_data["awaiting_answer_for"] = None # Clear the state
            self._save_learned_knowledge()
            self._save_user_data()
            return {"response": bot_response, "state": "learned", "requires_reward": False}

        # State 2: User is responding "yes" or "no" to the teaching prompt.
        if user_data.get("pending_question_to_learn"):
            question = user_data["pending_question_to_learn"]
            if normalized_input == "yes":
                # Transition to the next state: waiting for the answer
                user_data["awaiting_answer_for"] = question
                user_data["pending_question_to_learn"] = None
                bot_response = "Great! What should the answer be?"
                self._save_user_data()
                return {"response": bot_response, "state": "learning_answer", "requires_reward": False}
            elif normalized_input == "no":
                # Cancel the learning process
                user_data["pending_question_to_learn"] = None
                bot_response = "Okay, no problem. What else can I help with?"
                self._save_user_data()
                return {"response": bot_response, "state": "learning_cancelled", "requires_reward": False}
            else:
                # If user types something other than yes/no, prompt again.
                bot_response = f"Please answer with 'yes' or 'no'. Do you want to teach me the answer to '{question}'?"
                return {"response": bot_response, "state": "fallback_teach_prompt", "requires_reward": False}


        # --- Standard Response Logic ---
        # 1. Handle specific name-related rules
        if "my name is " in user_input.lower():
            try:
                name = user_input.lower().split("my name is ")[1].strip().capitalize()
                user_data["name"] = name
                bot_response = random.choice(rules["my name is "]).format(name=name)
                current_state = "my name is "
            except IndexError:
                pass # Fall through to keyword search
        elif "what is my name" in user_input.lower():
            if user_data.get("name"):
                bot_response = random.choice(rules["what is my name"]).format(name=user_data["name"])
                current_state = "what is my name"

        # 2. Use NLP keyword matching if no specific rule has matched yet
        if not bot_response:
            best_match, source, score = self._find_best_match_by_keywords(normalized_input)
            # We require at least one keyword to match to be confident
            if score > 0 and best_match:
                current_state = best_match
                if source == 'rules':
                    # If the match is a rule, use Q-Learning to pick a response
                    bot_response = self._choose_action(current_state)
                elif source == 'learned_knowledge':
                    # If it's something learned, give the direct answer
                    bot_response = self.learned_knowledge[best_match]
        
        # 3. Fallback: If no response found, trigger the active learning process
        if not bot_response:
            current_state = "fallback_teach_prompt" 
            # Set the pending state for the *next* turn, storing the raw user input
            user_data["pending_question_to_learn"] = user_input 
            bot_response = f"I don't have an answer for '{user_input}'. Do you want to teach me? (yes/no)"
            self._save_user_data()
            # This is a prompt, not a final answer, so it doesn't need a reward.
            return {"response": bot_response, "state": current_state, "requires_reward": False}

        # --- Save State for Q-Learning ---
        # Store state for next turn's reward update
        user_data["last_state"] = current_state
        user_data["last_action"] = bot_response
        self._save_user_data()

        return {"response": bot_response, "state": current_state, "requires_reward": True}

    def provide_feedback(self, user_id, reward):
        """Applies reward to the last state-action pair for a user."""
        user_data = self.all_users_data.get(user_id)
        if not user_data or not user_data.get("last_state") or not user_data.get("last_action"):
            return "Could not apply reward. No previous action found for this user."

        last_state = user_data["last_state"]
        last_action = user_data["last_action"]
        
        # In a real-time chat, the 'next_state' is unknown until the user's next message.
        # We can pass a placeholder to the Q-table update function.
        self._update_q_table(last_state, last_action, reward, "unknown_next_state")

        # Clear last action to prevent rewarding twice
        user_data["last_state"] = None
        user_data["last_action"] = None
        self._save_user_data()

        return f"Thanks for the feedback! Reward of {reward} applied."