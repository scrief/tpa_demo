# Deploying TPA Match Demo to Streamlit Cloud

## Step-by-Step Deployment Guide

### Prerequisites ✅

1. **GitHub Repository**: Your code is already on GitHub at `github.com/scrief/tpa_demo`
2. **Streamlit Cloud Account**: Sign up at [share.streamlit.io](https://share.streamlit.io)

---

## Deployment Steps

### 1. Sign Up / Log In to Streamlit Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Click **"Sign in with GitHub"**
3. Authorize Streamlit to access your GitHub repositories

### 2. Create New App

1. Click the **"New app"** button
2. Choose your repository: `scrief/tpa_demo`
3. Select branch: `main`
4. Main file path: `app.py`
5. (Optional) Custom app URL

### 3. Configure Secrets (IMPORTANT!)

Before deploying, click **"Advanced settings"** → **"Secrets"**

Paste this into the secrets editor:

```toml
AI_PROVIDER = "gemini"
GOOGLE_API_KEY = "AIzaSyBqCb-7CH3wUHqJeAkJYwBdbDKGpTRkLOE"
GEMINI_PARSING_MODEL = "gemini-2.5-flash"
GEMINI_EXPLANATION_MODEL = "gemini-2.5-flash"
AI_FEATURES_ENABLED = "true"
```

### 4. Deploy!

Click **"Deploy"** button

Your app will:
- Install dependencies from `requirements.txt`
- Start the app
- Be available at your custom URL (e.g., `your-app-name.streamlit.app`)

---

## ⚠️ IMPORTANT: Pre-Deployment Security Checklist

### Before Your App Goes Live:

1. **Remove Demo Accounts** (if not already done):
   ```bash
   python scripts/remove_demo_users.py
   git add database/tpa_match_demo.db
   git commit -m "Remove demo accounts for production"
   git push
   ```

2. **Verify .env is NOT in git**:
   ```bash
   git ls-files | grep .env
   ```
   (Should show nothing - .env should not be tracked)

3. **Check .gitignore includes**:
   ```
   .env
   *.db-journal
   __pycache__/
   *.pyc
   .streamlit/secrets.toml
   ```

---

## Post-Deployment Steps

### 1. Test Your App

Visit your app URL and test:
- [ ] Login page appears
- [ ] Can create new account (sign up works)
- [ ] Can log in successfully
- [ ] All navigation works (Home, New Match, Results, Vendors)
- [ ] AI parsing works (if enabled)
- [ ] Match generation works
- [ ] Results display correctly

### 2. Create Your Admin Account

Since demo accounts should be removed:
1. Use the **Sign Up** tab to create your account
2. Document credentials in a password manager

### 3. (Optional) Disable Public Signup

If you want only specific people to have access, you can disable the signup form after creating your accounts.

---

## Database on Streamlit Cloud

**Important:** Streamlit Cloud is **ephemeral** - your SQLite database will reset when:
- The app restarts
- You redeploy
- The container is recycled

### Solutions:

**Option 1: Include Database in Git** (Current Setup)
- Database is committed to git (`database/tpa_match_demo.db`)
- Any new users or data will be lost on restart
- Good for: Demos, read-only apps

**Option 2: External Database** (Recommended for Production)
- Use PostgreSQL, MySQL, or MongoDB
- Data persists across restarts
- Options:
  - [Supabase](https://supabase.com) (Free tier available)
  - [PlanetScale](https://planetscale.com) (MySQL)
  - [MongoDB Atlas](https://www.mongodb.com/cloud/atlas) (Free tier)
  - [Neon](https://neon.tech) (PostgreSQL)

**Option 3: Streamlit Cloud + Persistence**
- Mount persistent storage (Enterprise feature)
- Use Streamlit's connection feature with external DB

---

## Updating Your Deployed App

After making changes locally:

```bash
# 1. Commit your changes
git add .
git commit -m "Description of changes"

# 2. Push to GitHub
git push origin main

# 3. Streamlit will automatically detect the push and redeploy!
```

**Auto-deploy happens within 1-2 minutes of pushing to GitHub.**

---

## Managing Your Deployment

### Access App Settings

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Click on your app
3. Click the ⚙️ **Settings** icon

### Available Options:

- **Secrets**: Update environment variables
- **Resources**: View/upgrade compute resources
- **Logs**: View application logs for debugging
- **Analytics**: See usage statistics
- **Delete app**: Remove deployment

### View Logs

Click **"Manage app"** → **"Logs"** to see:
- Startup messages
- Print statements
- Errors
- User activity

---

## Common Issues & Solutions

### Issue: "ModuleNotFoundError"
**Solution:** Make sure all dependencies are in `requirements.txt`

### Issue: Database resets on restart
**Solution:** Either:
1. Commit database to git before each push, or
2. Switch to external database

### Issue: Secrets not loading
**Solution:** 
- Check TOML format (no typos)
- Verify quotes around string values
- Restart app after updating secrets

### Issue: App is slow to load
**Solution:**
- Streamlit Cloud has resource limits on free tier
- Consider caching with `@st.cache_data`
- Upgrade to higher tier if needed

### Issue: Can't log in after deployment
**Solution:**
- Make sure you've created at least one user account
- Check that `create_users_table.py` ran successfully
- Verify database file exists in git

---

## Cost & Limits (Free Tier)

**Streamlit Cloud Free Tier Includes:**
- 1 GB RAM
- 1 CPU core
- Unlimited public apps
- Community support

**Limitations:**
- Apps sleep after 7 days of inactivity
- Limited compute resources
- No custom domains (without upgrade)

---

## Optional: Custom Domain

If you have a custom domain:

1. Upgrade to Team or Enterprise plan
2. Configure DNS settings
3. Add domain in Streamlit Cloud settings

---

## Security Best Practices

1. ✅ **Never commit `.env` files**
2. ✅ **Use Streamlit secrets for sensitive data**
3. ✅ **Remove demo accounts before going live**
4. ✅ **Use strong passwords for production accounts**
5. ✅ **Keep dependencies updated**
6. ✅ **Monitor logs for suspicious activity**
7. ✅ **Consider disabling public signup**
8. ✅ **Rotate API keys periodically**

---

## Quick Deployment Checklist

- [ ] Code pushed to GitHub (main branch)
- [ ] Demo accounts removed (or keep for demo purposes)
- [ ] `.env` not in git
- [ ] `requirements.txt` up to date
- [ ] Streamlit Cloud account created
- [ ] App deployed with secrets configured
- [ ] Test login/signup works
- [ ] Create admin account
- [ ] Test all features
- [ ] Monitor logs for errors

---

## Need Help?

**Streamlit Community:**
- [Community Forum](https://discuss.streamlit.io)
- [Documentation](https://docs.streamlit.io)
- [Deploy Guide](https://docs.streamlit.io/streamlit-community-cloud/deploy-your-app)

**Your App URLs:**
- GitHub Repo: `https://github.com/scrief/tpa_demo`
- Streamlit Cloud: `https://share.streamlit.io` (after deployment)
- Your App: Will be `https://[your-app-name].streamlit.app`

---

🚀 **Ready to Deploy!** Follow the steps above and your app will be live in minutes!
