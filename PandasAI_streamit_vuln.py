import openai
import streamlit as st

import getpass
import os
import sys
import pandas as pd
from langchain_community.llms import Ollama
from pandasai import SmartDataframe



if 'message_list' not in st.session_state:
  st.session_state.message_list = [
      {"role": "system", "content": "You are a helpful assistant."}
    ]      

class Conversaion:
  
  def __init__(self):
    pass
        
  def message(self, question):
    
    q = {
      "role": "user",
      "content": question
    }
        
    st.session_state.message_list.append(q)
    


    llm = Ollama(base_url='http://192.168.1.144:11434', model="deepseek-r1:14b")
    data = pd.read_csv("metasploit_3.csv")
    #data = pd.read_csv("ds_salaries.csv")
    data.head()


    df = SmartDataframe(data, config={"llm": llm})
    


    response =  df.chat(question)
    
    q = {
      "role": "assistant",
      "content": response
    }
    
    st.session_state.message_list.append(q)
    
    return response
  

if __name__ == "__main__":
  
  st.title('Welcome to  AI-powered Data Analysis Platform!')

  message = st.chat_message("assistant")
  

  message.write("Leveraging artificial intelligence (AI) technologies to automate, enhance, and scale the process of analyzing data.")

  message.write("In combination with machine learning (ML), natural language processing (NLP), and computer vision to extract meaningful insights from large and complex datasets.")
  conversation = Conversaion()
  
  prompt = st.chat_input("Ask a question")
  if prompt:
    
    with st.spinner('Thinking...'):
            
      answer = conversation.message(prompt)
            
      for l in st.session_state.message_list:
        
        print(l)
        
        if l['role'] == 'user':
          with st.chat_message("user"):
            st.write(l['content'])
        elif l['role'] == 'assistant':
          with st.chat_message("assistant"):
            st.write(l['content'])
