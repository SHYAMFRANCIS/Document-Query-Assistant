# 🚀 Deployment Guide

Complete guide for deploying Document Query Assistant to Streamlit Cloud.

## 📋 Prerequisites

- GitHub account
- Google Gemini API key ([Get one free](https://aistudio.google.com/app/apikey))
- Document Query Assistant repository on GitHub

---

## 🌟 Deploy to Streamlit Cloud (Recommended)

### Step 1: Prepare Your Repository

1. Ensure your code is pushed to GitHub:
   ```bash
   git add .
   git commit -m "Prepare for Streamlit Cloud deployment"
   git push origin main
   ```

2. Verify these files exist in your repository:
   - ✅ `requirements.txt` - Python dependencies
   - ✅ `app.py` - Main application file
   - ✅ `.streamlit/config.toml` - Streamlit configuration
   - ⚠️ `.streamlit/secrets.toml` - **DO NOT commit this** (contains API key)

### Step 2: Get Gemini API Key

1. Visit [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the generated API key (looks like: `AIzaSy...`)

### Step 3: Deploy on Streamlit Cloud

1. Go to [Streamlit Community Cloud](https://share.streamlit.io/)
2. Click **"Sign in"** (use your GitHub account)
3. Click **"New app"**
4. Fill in the deployment form:
   - **Repository**: Select your `Document-Query-Assistant` repo
   - **Branch**: `main` (or `master`)
   - **Main file path**: `app.py`
5. Click **"Advanced settings"**
6. Add your API key:
   ```toml
   [gemini]
   api_key = "AIzaSy YOUR ACTUAL API KEY HERE"
   ```
7. Click **"Deploy!"**

### Step 4: Access Your App

- Your app will be available at: `https://your-app-name.streamlit.app`
- Deployment takes 1-3 minutes
- You'll see a live preview during deployment

---

## 🔒 Security Best Practices

### ✅ DO:
- Store API keys in Streamlit Cloud secrets (Advanced settings)
- Use `.streamlit/secrets.toml` for local development
- Keep `.env` file for local testing
- Rotate API keys periodically

### ❌ DON'T:
- **NEVER commit** `.streamlit/secrets.toml` to GitHub
- **NEVER commit** `.env` file with real API keys
- **NEVER share** API keys in public repositories
- **NEVER hardcode** API keys in source code

---

## 🛠️ Local Development

### Setup Local Environment

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/Document-Query-Assistant.git
   cd Document-Query-Assistant
   ```

2. Install dependencies with uv:
   ```bash
   uv sync
   ```

3. Configure API key (choose one method):

   **Option A: Streamlit secrets (Recommended)**
   ```bash
   # Edit .streamlit/secrets.toml
   [gemini]
   api_key = "your_api_key_here"
   ```

   **Option B: Environment variable**
   ```bash
   # Create .env file
   echo "GEMINI_API_KEY=your_api_key_here" > .env
   ```

4. Run the app:
   ```bash
   uv run streamlit run app.py
   ```

5. Open browser: `http://localhost:8501`

---

## 🔄 Updating Your Deployment

### Automatic Updates

Streamlit Cloud can auto-deploy on push to GitHub:

1. Go to your app dashboard on Streamlit Cloud
2. Click **"Settings"**
3. Enable **"Auto-deploy on push"**
4. Select branch: `main`

### Manual Deployment

```bash
# Make your changes
git add .
git commit -m "Update feature"
git push origin main

# Streamlit Cloud will auto-deploy in 1-2 minutes
```

---

## 🐛 Troubleshooting

### App won't deploy

**Check the deployment logs:**
1. Go to Streamlit Cloud dashboard
2. Click your app
3. Click **"Manage app"** → **"Logs"**

**Common issues:**

| Issue | Solution |
|-------|----------|
| `ModuleNotFoundError` | Ensure `requirements.txt` includes all dependencies |
| `API key not configured` | Check secrets in Advanced settings |
| `File not found` | Verify file paths are correct |
| `ImportError` | Make sure all imports match your file structure |

### App crashes after update

1. Check deployment logs for errors
2. Rollback to previous commit:
   ```bash
   git log --oneline
   git revert <commit-hash>
   git push origin main
   ```

### API key not working

1. Verify API key is valid at [Google AI Studio](https://aistudio.google.com/)
2. Check for typos in secrets configuration
3. Ensure proper TOML format in secrets

---

## 📊 Monitoring & Analytics

### Streamlit Cloud Dashboard

- View app status (Running/Stopped)
- Check deployment logs
- Manage secrets and settings
- Configure auto-deploy

### Google AI Studio

- Monitor API key usage
- View request counts and errors
- Manage multiple API keys
- Set usage quotas

---

## 💰 Pricing & Limits

### Streamlit Community Cloud (Free)
- ✅ Unlimited apps
- ✅ 1 GB memory per app
- ✅ Auto-sleep after inactivity
- ✅ Community support
- ⚠️ Apps sleep after 1 hour of inactivity
- ⚠️ Wake-up time: 10-30 seconds

### Google Gemini API (Free Tier)
- ✅ 15 RPM (requests per minute)
- ✅ 1 million tokens per minute
- ✅ 1,500 requests per day
- 💲 Pay-as-you-go after free tier

---

## 🚀 Production Checklist

Before going live:

- [ ] API key stored in Streamlit secrets (not hardcoded)
- [ ] `.streamlit/secrets.toml` added to `.gitignore`
- [ ] All dependencies in `requirements.txt`
- [ ] App tested locally
- [ ] Error handling implemented
- [ ] README updated with usage instructions
- [ ] Auto-deploy enabled on Streamlit Cloud
- [ ] Tested with sample documents
- [ ] Share app URL with users

---

## 📞 Support

- **Streamlit Community**: [discuss.streamlit.io](https://discuss.streamlit.io/)
- **Streamlit Docs**: [docs.streamlit.io](https://docs.streamlit.io/)
- **Google Gemini**: [ai.google.dev/docs](https://ai.google.dev/docs)
- **GitHub Issues**: Report bugs in your repository

---

## 🎯 Next Steps

1. **Share your app**: Copy the URL from Streamlit Cloud
2. **Custom domain**: Streamlit Cloud supports custom domains (Pro feature)
3. **Collaborate**: Add team members in Streamlit Cloud settings
4. **Monitor usage**: Track API usage in Google AI Studio

---

**Happy deploying! 🎉**
