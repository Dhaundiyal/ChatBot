import json
import numpy as np
import streamlit as st
from difflib import get_close_matches
from keras.models import load_model, Model
from keras.layers import Input
from keras.layers import Input, LSTM, Dense
import re
import time
import keyboard
import os
import psutil
try:
    from googlesearch import search
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    print("No module")

class ChatBot:
    def __init__(self):
        # Load the seq2seq model
        self.training_model = load_model('training_model.h5')
        encoder_inputs = self.training_model.input[0]
        encoder_outputs, state_h_enc, state_c_enc = self.training_model.layers[2].output
        encoder_states = [state_h_enc, state_c_enc]
        self.encoder_model = Model(encoder_inputs, encoder_states)

        latent_dim = 256
        decoder_state_input_hidden = Input(shape=(latent_dim,))
        decoder_state_input_cell = Input(shape=(latent_dim,))
        decoder_states_inputs = [decoder_state_input_hidden, decoder_state_input_cell]
        #Decoder
        dimensionality = 256 
        num_decoder_tokens = 3101
        decoder_inputs = Input(shape=(None, num_decoder_tokens))
        decoder_lstm = LSTM(dimensionality, return_sequences=True, return_state=True)
        decoder_outputs, decoder_state_hidden, decoder_state_cell = decoder_lstm(decoder_inputs, initial_state=encoder_states)
        decoder_dense = Dense(num_decoder_tokens, activation='softmax')
        decoder_outputs = decoder_dense(decoder_outputs)
        # Assuming that you have the decoder_lstm and decoder_dense layers defined somewhere
        decoder_outputs, state_hidden, state_cell = decoder_lstm(decoder_inputs, initial_state=decoder_states_inputs)
        decoder_states = [state_hidden, state_cell]
        decoder_outputs = decoder_dense(decoder_outputs)
        self.decoder_model = Model([decoder_inputs] + decoder_states_inputs, [decoder_outputs] + decoder_states)

        # Load the knowledge base
        self.knowledge_base = self.load_knowledge_base('knowledge_base.json')
        self.question_dict = self.build_question_dict(self.knowledge_base["questions"])

        self.negative_responses = ("no", "nope", "nah", "naw", "not a chance", "sorry")
        self.exit_commands = ("quit", "pause", "exit", "goodbye", "bye", "later", "stop")

    def load_knowledge_base(self, file_path: str) -> dict:
        with open(file_path, 'r', encoding='utf-8') as file:
            data: dict = json.load(file)
        return data

    def build_question_dict(self, questions: list) -> dict:
        return {q["Question"]: q["Answer"] for q in questions}

    def save_knowledge_base(self, file_path: str, data: dict):
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=2)

    def find_best_match(self, user_question: str) -> str | None:
        matches: list = get_close_matches(user_question, self.question_dict.keys(), n=1, cutoff=0.6)
        return matches[0] if matches else None

    def get_answer_for_question(self, question: str) -> str | None:
        return self.question_dict.get(question)


    def run_chat_bot(self, user_input, user_provided_answer=None):
        if user_input.lower() == 'quit':
            return "Bye! Have a great day ahead"

        best_match = self.find_best_match(user_input)

        if best_match:
            answer = self.get_answer_for_question(best_match)
            return f'Bot: {answer}'
        else:
            query = user_input
            for link in search(query, tld="co.in", num=10, stop=10, pause=2):
                try:
                    response = requests.get(link)
                    soup = BeautifulSoup(response.text, 'html.parser')
                    paragraphs = soup.find_all('p')[:3]

                    if paragraphs:
                        relevant_info = '\n'.join(p.get_text() for p in paragraphs)
                        break  
                    else:
                        pass
                except Exception as e:
                    return(f"Error processing\n")
            new_answer = relevant_info
            self.knowledge_base["questions"].append({"Question": user_input, "Answer": new_answer})
            self.question_dict = self.build_question_dict(self.knowledge_base["questions"])
            self.save_knowledge_base('knowledge_base.json', self.knowledge_base)
            return new_answer+"\n"+link


chatbot = ChatBot()


def main():
    st.title("Mental Health Therapist Chatbot")
    exit_app = st.sidebar.button("Shut Down")
    if exit_app:
        time.sleep(5)
        keyboard.press_and_release('ctrl+w')
        # Terminate streamlit python process
        pid = os.getpid()
        p = psutil.Process(pid)
        p.terminate()
    user_input = st.text_input("How can I help you")
    
    if user_input:
        bot_response = chatbot.run_chat_bot(user_input)
        st.write(bot_response)



if __name__ == "__main__":
    main()
