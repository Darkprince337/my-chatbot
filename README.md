# 🤖 Reinforcement Learning Chatbot Web App

<p align="center">
  <img src="https://readme-typing-svg.herokuapp.com?size=30&color=00FFCC&center=true&vCenter=true&width=900&lines=AI+Chatbot+with+Reinforcement+Learning;Self+Learning+System;Built+with+Flask+%26+Python;Improves+with+User+Feedback" />
</p>

<p align="center">

![Python](https://img.shields.io/badge/Python-3.10-blue?style=for-the-badge&logo=python)
![Flask](https://img.shields.io/badge/Flask-Web%20Framework-black?style=for-the-badge&logo=flask)
![AI](https://img.shields.io/badge/AI-Reinforcement%20Learning-green?style=for-the-badge)
![HTML](https://img.shields.io/badge/HTML-Frontend-orange?style=for-the-badge&logo=html5)
![CSS](https://img.shields.io/badge/CSS-Styling-blue?style=for-the-badge&logo=css3)
![JavaScript](https://img.shields.io/badge/JavaScript-Client%20Side-yellow?style=for-the-badge&logo=javascript)

</p>

---

## 📌 Overview

This project is an **AI-powered chatbot** built using **Flask, Python, and Reinforcement Learning (Q-Learning)** with a **frontend developed using HTML, CSS, and JavaScript**.

Unlike traditional chatbots, this system can:

✔ Learn from user feedback  
✔ Improve responses over time  
✔ Store new knowledge dynamically  
✔ Provide personalized conversations  

---

## ✨ Features

### 🔐 Authentication System
- User registration & login
- Password hashing using Werkzeug
- Secure JSON storage

### 💬 Chat System
- Real-time chat interface
- Dynamic message rendering using JavaScript
- User-specific conversation tracking
- REST API based communication

### 🧠 Reinforcement Learning (Q-Learning)
- Learns from user feedback (reward/penalty)
- Stores Q-values for better decisions
- Exploration vs exploitation strategy

### 📚 Self-Learning Capability
- Asks users to teach unknown answers
- Stores learned knowledge
- Uses it in future conversations

### 🔍 NLP Processing
- Text normalization
- Keyword extraction
- Stopword removal
- Smart matching

### ⭐ Feedback System
- Users rate responses
- Updates Q-table dynamically

### 🎨 Frontend (HTML, CSS, JavaScript)
- Responsive UI using HTML & CSS
- Dynamic chat updates using JavaScript
- API communication using Fetch/AJAX
- Interactive user experience

### 💾 Persistent Storage
- Q-table
- User data
- Learned knowledge
- Stored in JSON files

---

## 🧠 How It Works

```text
User Input → Normalize Text → Extract Keywords
          ↓
Find Best Match (Rules / Learned Knowledge)
          ↓
Select Response (Q-Learning)
          ↓
Send Response (via Flask API)
          ↓
Frontend (JS) Displays Message
          ↓
User Feedback → Update Q-Table
