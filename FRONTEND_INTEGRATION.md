# 🌐 Frontend Integration Test Guide

## ✅ CORS Configuration Complete!

Your FastAPI backend is now configured to accept requests from your frontend at `http://localhost:3000`.

### 🔧 What I've Updated:

1. **CORS Settings**: Updated to allow your frontend origin
2. **Methods**: Added `OPTIONS` method for preflight requests
3. **Headers**: Configured to allow all headers and credentials
4. **Environment**: Set up `.env` file with proper CORS origins

### 🧪 Test Your Connection

Here's a simple test you can run in your frontend:

#### JavaScript/React Test:
```javascript
// Test 1: Health Check
const testConnection = async () => {
  try {
    const response = await fetch('http://127.0.0.1:8000/health');
    const data = await response.json();
    console.log('✅ Connection successful:', data);
  } catch (error) {
    console.error('❌ Connection failed:', error);
  }
};

// Test 2: API Info
const testAPIInfo = async () => {
  try {
    const response = await fetch('http://127.0.0.1:8000/');
    const data = await response.json();
    console.log('✅ API Info:', data);
  } catch (error) {
    console.error('❌ API Info failed:', error);
  }
};

// Test 3: Create Anonymous Link
const testCreateLink = async () => {
  try {
    const response = await fetch('http://127.0.0.1:8000/links/create', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        url: 'https://example.com'
      })
    });
    const data = await response.json();
    console.log('✅ Link created:', data);
  } catch (error) {
    console.error('❌ Link creation failed:', error);
  }
};

// Run tests
testConnection();
testAPIInfo();
testCreateLink();
```

#### React Axios Example:
```javascript
import axios from 'axios';

// Configure base URL
const api = axios.create({
  baseURL: 'http://127.0.0.1:8000',
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json',
  }
});

// Test connection
const testAPI = async () => {
  try {
    const health = await api.get('/health');
    console.log('✅ API Health:', health.data);
    
    const info = await api.get('/');
    console.log('✅ API Info:', info.data);
  } catch (error) {
    console.error('❌ API Test Failed:', error);
  }
};
```

### 🔑 Authentication Example:
```javascript
// Login and get token
const login = async (email, password) => {
  try {
    const response = await fetch('http://127.0.0.1:8000/auth/login', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ email, password })
    });
    
    const data = await response.json();
    
    if (response.ok) {
      // Store token
      localStorage.setItem('access_token', data.access_token);
      localStorage.setItem('refresh_token', data.refresh_token);
      console.log('✅ Login successful');
      return data;
    } else {
      console.error('❌ Login failed:', data.detail);
    }
  } catch (error) {
    console.error('❌ Login error:', error);
  }
};

// Use authenticated endpoint
const getMyLinks = async () => {
  const token = localStorage.getItem('access_token');
  
  try {
    const response = await fetch('http://127.0.0.1:8000/links/my-links', {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });
    
    const data = await response.json();
    console.log('✅ My links:', data);
    return data;
  } catch (error) {
    console.error('❌ Failed to get links:', error);
  }
};
```

### 🚀 Start Your Servers:

1. **Backend (FastAPI)**:
   ```bash
   cd "c:\Users\Noor\Desktop\FASTAPI Auth\myapp"
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

2. **Frontend** (on port 3000):
   ```bash
   # React
   npm start
   
   # Next.js
   npm run dev
   
   # Vite
   npm run dev
   ```

### 🔍 Troubleshooting:

If you encounter CORS issues:

1. **Check Console**: Look for CORS errors in browser console
2. **Verify Origins**: Make sure your frontend is running on `localhost:3000`
3. **Restart Backend**: After changing CORS settings, restart FastAPI
4. **Browser Cache**: Clear browser cache or use incognito mode

### 📱 Mobile/Different Ports:

If you need to test from different ports or devices, update the `.env` file:

```env
# Add more origins as needed
ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000,http://localhost:3001,http://192.168.1.100:3000
```

### 🎯 Production Deployment:

For production, update your `.env`:

```env
ENVIRONMENT=production
DEBUG=false
ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

---

Your API is now ready to connect with your frontend at `http://localhost:3000`! 🎉
