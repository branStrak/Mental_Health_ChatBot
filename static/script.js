document.addEventListener('DOMContentLoaded', () => {
  // Define elements with null checks
  const themeToggleBtn = document.getElementById('theme-toggle');
  const toggleSidebarBtn = document.getElementById('toggle-sidebar');
  const sidebar = document.getElementById('sidebar');
  const sidebarOverlay = document.getElementById('sidebar-overlay');
  const newConversationBtn = document.getElementById('new-conversation');
  const conversationList = document.getElementById('conversation-list');
  const chatTitle = document.getElementById('chat-title');
  const chatInput = document.getElementById('chat-input');
  const sendButton = document.getElementById('send-button');
  const chatForm = document.getElementById('chat-form');
  const welcomeScreen = document.getElementById('welcome-screen');
  const messageContainer = document.getElementById('message-container');
  const signInBtn = document.getElementById('sign-in-btn');
  const signUpBtn = document.querySelector('.sign-up-btn');
  const signOutBtn = document.getElementById('sign-out-btn');
  const signOutBtn1 = document.getElementById('sign-out-btn1');
  const authButtons = document.getElementById('auth-buttons');
  const modelSelector = document.getElementById('model-selector');

  let conversations = [];
  let activeConversationId = null;
  let isTyping = false;

  // Utility functions
  function generateId() {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
      const r = Math.random() * 16 | 0, v = c == 'x' ? r : (r & 0x3 | 0x8);
      return v.toString(16);
    });
  }

  // Theme toggle functionality
  function initTheme() {
    if (!themeToggleBtn) return;
    const themeIcon = themeToggleBtn.querySelector('i');
    const savedTheme = localStorage.getItem('theme');
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;

    if (savedTheme === 'dark' || (!savedTheme && prefersDark)) {
      document.documentElement.classList.add('dark');
      themeIcon.classList.remove('fa-moon');
      themeIcon.classList.add('fa-sun');
    } else {
      document.documentElement.classList.remove('dark');
      themeIcon.classList.remove('fa-sun');
      themeIcon.classList.add('fa-moon');
    }
  }

  function toggleTheme() {
    if (!themeToggleBtn) return;
    const themeIcon = themeToggleBtn.querySelector('i');
    const isDarkMode = document.documentElement.classList.toggle('dark');
    themeIcon.classList.toggle('fa-sun', isDarkMode);
    themeIcon.classList.toggle('fa-moon', !isDarkMode);
    localStorage.setItem('theme', isDarkMode ? 'dark' : 'light');
  }

  // Sidebar
  function toggleSidebar() {
    if (!sidebar || !sidebarOverlay) return;
    const isOpen = sidebar.classList.toggle('open');
    sidebarOverlay.classList.toggle('open', isOpen);
  }

  // Chat functions
  function renderConversationList() {
    if (!conversationList) return;
    conversationList.innerHTML = '';
    if (conversations.length === 0) {
      const emptyItem = document.createElement('li');
      emptyItem.className = 'conversation-item-empty';
      emptyItem.textContent = 'No conversations yet';
      conversationList.appendChild(emptyItem);
      return;
    }
    conversations.forEach(conversation => {
      const li = document.createElement('li');
      li.className = `conversation-item ${activeConversationId === conversation.id ? 'active' : ''}`;
      li.dataset.id = conversation.id;
      li.innerHTML = `
        <div class="conversation-item-icon">
          <i class="fa-solid fa-message"></i>
        </div>
        <div class="conversation-item-content">
          <div class="conversation-item-title">${conversation.title}</div>
          <div class="conversation-item-preview">${conversation.lastMessage}</div>
        </div>
      `;
      conversationList.appendChild(li);
    });
  }

  function renderMessages(conversationId) {
    // console.log("📨 Rendering messages for conversation:", conversationId);

    if (!welcomeScreen || !messageContainer) return;
  
    const conversation = conversations.find(c => String(c.id) === String(conversationId));
    // console.log("💬 Messages in selected conversation:", conversation.messages);
    if (!conversation) {
      welcomeScreen.style.display = 'flex';
      messageContainer.style.display = 'none';
      return;
    }
  
    welcomeScreen.style.display = 'none';
    messageContainer.style.display = 'block';
    messageContainer.innerHTML = '';
  
    conversation.messages.forEach(message => {
      const messageEl = createMessageElement({
        id: message.id,
        content: message.content || message.text, // support both formats
        sender: message.sender,
        timestamp: message.timestamp ? new Date(message.timestamp) : new Date()
      });
      messageContainer.appendChild(messageEl);
    });
  
    scrollToBottom();
  }
  
  

  function createMessageElement(message) {
    if (!messageContainer) return document.createElement('div');
    const messageEl = document.createElement('div');
    messageEl.className = `message message-${message.sender}`;
    const isBotMessage = message.sender === 'bot';
    messageEl.innerHTML = `
      ${isBotMessage ? `<div class="message-avatar"><i class="fa-solid fa-brain"></i></div>` : ''}
      <div class="message-bubble message-bubble-${message.sender}">
        ${message.content || message.text}
      </div>
      ${!isBotMessage ? `<div class="message-avatar"><i class="fa-solid fa-user"></i></div>` : ''}
    `;
    return messageEl;
  }

  function createTypingIndicator() {
    if (!messageContainer) return document.createElement('div');
    const typingEl = document.createElement('div');
    typingEl.className = 'message message-bot';
    typingEl.innerHTML = `
      <div class="message-avatar">
        <i class="fa-solid fa-brain"></i>
      </div>
      <div class="message-bubble message-bubble-bot">
        <div class="typing-indicator">
          <span></span><span></span><span></span>
        </div>
      </div>
    `;
    return typingEl;
  }

  function scrollToBottom() {
    if (!messageContainer) return;
    const chatWindow = document.getElementById('chat-window');
    chatWindow.scrollTop = chatWindow.scrollHeight;
  }

  function selectConversation(conversationId) {
    if (!conversationList || !chatTitle) return;
  
    activeConversationId = conversationId;
    renderConversationList();
    renderMessages(conversationId);
  
    const conversation = conversations.find(c => c.id === conversationId);
    chatTitle.textContent = conversation ? conversation.title : 'New conversation';
  
    if (window.innerWidth <= 768 && sidebar.classList.contains('open')) {
      toggleSidebar();
    }
  }
  
  

  function createNewConversation() {
    if (!conversationList || !chatTitle) return;
    selectConversation(null);
  }

  function sendMessage(content) {
    if (!chatInput || !sendButton || !messageContainer || !modelSelector) return;
    if (!content.trim() || isTyping) return;
  
    const userId = localStorage.getItem('userId');
    const selectedModel = modelSelector.value;
    let endpoint = '/chat/chat';
    if (selectedModel === 'gemma') {
      endpoint = '/chat';
    }
  
    // Use current conversation ID or prepare for a new one
    let currentConversationId = activeConversationId;
    let isNewConversation = !currentConversationId;
  
    if (isNewConversation) {
      currentConversationId = generateId(); // temporary placeholder
      const newConversation = {
        id: currentConversationId,
        title: content.length > 20 ? `${content.substring(0, 20)}...` : content,
        lastMessage: 'Thinking...',
        date: new Date(),
        messages: []
      };
      conversations.unshift(newConversation);
      activeConversationId = currentConversationId;
      renderConversationList();
      chatTitle.textContent = newConversation.title;
      welcomeScreen.style.display = 'none';
      messageContainer.style.display = 'block';
    }
  
    const userMessage = {
      id: generateId(),
      content: content,
      sender: 'user',
      timestamp: new Date()
    };
  
    const conversation = conversations.find(c => c.id === currentConversationId);
    conversation.messages.push(userMessage);
    const userMessageEl = createMessageElement(userMessage);
    messageContainer.appendChild(userMessageEl);
    scrollToBottom();
  
    isTyping = true;
    sendButton.disabled = true;
    chatInput.disabled = true;
  
    const typingIndicator = createTypingIndicator();
    messageContainer.appendChild(typingIndicator);
    scrollToBottom();
  
    fetch(endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        prompt: content,
        user_id: userId,
        conversation_id: isNewConversation ? null : currentConversationId
      })
    })
      .then(res => res.json())
      .then(data => {
        const botMessage = {
          id: generateId(),
          content: data.response,
          sender: 'bot',
          timestamp: new Date()
        };
        messageContainer.removeChild(typingIndicator);
        conversation.messages.push(botMessage);
        const botMessageEl = createMessageElement(botMessage);
        messageContainer.appendChild(botMessageEl);
        scrollToBottom();
        conversation.lastMessage = botMessage.content;
        conversation.date = new Date();
  
        // Only update ID if it was a new conversation
        if (data.conversation_id) {
          conversation.id = data.conversation_id;
          activeConversationId = data.conversation_id;
        }
        
  
        renderConversationList();
        sendButton.disabled = false;
        chatInput.disabled = false;
        chatInput.focus();
        isTyping = false;
      })
      .catch(err => {
        console.error('Error:', err);
        messageContainer.removeChild(typingIndicator);
        const errorMsg = {
          id: generateId(),
          content: "⚠️ There was a problem contacting the AI. Please try again later.",
          sender: 'bot',
          timestamp: new Date()
        };
        conversation.messages.push(errorMsg);
        const errorEl = createMessageElement(errorMsg);
        messageContainer.appendChild(errorEl);
        sendButton.disabled = false;
        chatInput.disabled = false;
        chatInput.focus();
        isTyping = false;
      });
  }
  
  function fetchPreviousConversations() {
    const userId = localStorage.getItem('userId');
    if (!userId) return;
  
    fetch('/chat/conversations', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ user_id: userId })
    })
    .then(res => res.json())
    .then(data => {
      if (data.conversations) {
        conversations = data.conversations.map(conv => ({
          id: conv.id,
          title: conv.messages[0]?.text?.substring(0, 20) || 'Conversation',
          lastMessage: conv.messages.slice(-1)[0]?.text || '',
          messages: conv.messages.map(m => ({
            id: m.id,
            content: m.text,
            sender: m.sender,
            timestamp: new Date()
          }))
        }));
        
        renderConversationList();
      }
    })
    .catch(err => console.error('Failed to fetch conversations:', err));
  }
  

  // Auth functions
  function handleSignIn() {
    alert('Sign in functionality will be implemented here.');
  }

  function handleSignUp() {
    if (signUpBtn) {
      window.location.href = '/register';
    }
  }

  function handleSignOut() {
    localStorage.removeItem('isLoggedIn');
    localStorage.removeItem('userId');

    updateAuthButtons();
    window.location.href = '/';
  }

  // Event listeners
  function initEventListeners() {
    if (themeToggleBtn) themeToggleBtn.addEventListener('click', toggleTheme);
    if (toggleSidebarBtn) toggleSidebarBtn.addEventListener('click', toggleSidebar);
    if (sidebarOverlay) sidebarOverlay.addEventListener('click', toggleSidebar);
    if (newConversationBtn) newConversationBtn.addEventListener('click', createNewConversation);
    if (signInBtn) signInBtn.addEventListener('click', () => window.location.href = '/login');
    if (signUpBtn) signUpBtn.addEventListener('click', handleSignUp);
    if (signOutBtn) signOutBtn.addEventListener('click', handleSignOut);

    if (conversationList) conversationList.addEventListener('click', (e) => {
      const conversationItem = e.target.closest('.conversation-item');
      if (conversationItem) {
        const conversationId = conversationItem.dataset.id;
        selectConversation(conversationId);
      }
    });

    if (chatForm) chatForm.addEventListener('submit', (e) => {
      e.preventDefault();
      const message = chatInput.value;
      sendMessage(message);
      chatInput.value = '';
      updateSendButtonState();
    });

    if (chatInput) {
      chatInput.addEventListener('input', () => {
        updateSendButtonState();
        chatInput.style.height = 'auto';
        chatInput.style.height = chatInput.scrollHeight + 'px';
      });

      chatInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
          e.preventDefault();
          chatForm.dispatchEvent(new Event('submit'));
        }
      });
    }

    if (window) window.addEventListener('resize', () => {
      if (window.innerWidth > 768) {
        if (sidebar) sidebar.classList.remove('open');
        if (sidebarOverlay) sidebarOverlay.classList.remove('open');
      }
    });
  }

  function initLoginPage() {
    const loginForm = document.getElementById('login-form');
    const registerBtn = document.getElementById('register-btn');
    if (loginForm && registerBtn) {
      loginForm.addEventListener('submit', (e) => {
        e.preventDefault();
        const email = document.getElementById('email').value;
        const password = document.getElementById('password').value;

        fetch('/api/login', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ email, password })
        })
        .then(response => response.json())
        .then(data => {
          if (data.message) {
           // alert(data.message);
            localStorage.setItem('isLoggedIn', 'true');
            localStorage.setItem('userId', data.user_id);

            updateAuthButtons();
            window.location.href = '/';
          } else {
            alert(data.error || 'Login failed');
          }
        })
        .catch(error => {
          console.error('Error:', error);
          alert('An error occurred during login');
        });
      });

      registerBtn.addEventListener('click', () => {
        window.location.href = '/register';
      });
    }
  }

  function initRegisterPage() {
    const registerForm = document.getElementById('register-form');
    if (registerForm) {
      registerForm.addEventListener('submit', (e) => {
        e.preventDefault();
        const username = document.getElementById('username').value;
        const email = document.getElementById('email').value;
        const age = document.getElementById('age').value;
        const password = document.getElementById('password').value;
        const gender = document.getElementById('gender').value;

        fetch('/api/register', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ username, email, age, password, gender })
        })
        .then(response => response.json())
        .then(data => {
          if (data.message) {
            alert(data.message);
            id=data.user_id;
            localStorage.setItem('userId',id);
            localStorage.setItem('isLoggedIn', 'true'); // Moved back to client side
            updateAuthButtons();
            window.location.href = '/index';
          } else {
            alert(data.error || 'Registration failed');
          }
        })
        .catch(error => {
          console.error('Error:', error);
          alert('An error occurred during registration');
        });
      });
    }
  }

  function updateSendButtonState() {
    if (sendButton && chatInput) {
      sendButton.disabled = !chatInput.value.trim() || isTyping;
    }
  }



  // Init and update auth buttons
  function updateAuthButtons() {
    const isLoggedIn = localStorage.getItem('isLoggedIn') === 'true';
    if (authButtons) {
      if (isLoggedIn) {
        if (signInBtn) signInBtn.style.display = 'none';
        if (signUpBtn) signUpBtn.style.display = 'none';
        if (themeToggleBtn) themeToggleBtn.style.display = 'inline-block';
        if (signOutBtn) signOutBtn.style.display = 'inline-block';
        if (signOutBtn1) signOutBtn.style.display = 'inline-block';


        fetchPreviousConversations();
      } else {
        if (signInBtn) signInBtn.style.display = 'inline-block';
        if (signUpBtn) signUpBtn.style.display = 'inline-block';
        if (themeToggleBtn) themeToggleBtn.style.display = 'inline-block';
        if (signOutBtn) signOutBtn.style.display = 'none';
        if (signOutBtn1) signOutBtn.style.display = 'none';

      }
    }
  }

  function init() {
    initTheme();
    initEventListeners();
    if (conversationList) renderConversationList();
    if (welcomeScreen && messageContainer) selectConversation(null);
    updateSendButtonState();
    updateAuthButtons();
    
    if (sidebar) sidebar.classList.remove('open');
    if (sidebarOverlay) sidebarOverlay.classList.remove('open');
    
    initLoginPage();
    initRegisterPage();
    
    console.log('✅ Serenity AI initialized');
  }

  init();
});