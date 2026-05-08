# Production Deployment Checklist

## Security Preparation

### 1. Remove Demo Accounts ✅
```bash
python scripts/remove_demo_users.py
```
This will permanently delete the `demo` and `admin` demo accounts.

**After removal:**
- Create a new admin account using the signup form
- Document the admin credentials securely (use a password manager)

### 2. Verify Environment Variables
Check your `.env` file:
- ✅ Remove or rotate any API keys that were shared/committed
- ✅ Use production API keys (not test/dev keys)
- ✅ Ensure `.env` is in `.gitignore` (never commit to git)

### 3. Update `.gitignore`
Ensure these files are NOT committed:
```
.env
*.db
__pycache__/
*.pyc
```

### 4. Database Security
```bash
# Backup your database
cp database/tpa_match_demo.db database/tpa_match_demo_backup.db

# Verify no sensitive test data exists
# Review all tables for test/dummy data
```

## Application Configuration

### 5. Update Branding/Content
- [ ] Update page titles and descriptions
- [ ] Remove "Demo" references if deploying as production
- [ ] Update company/contact information
- [ ] Add privacy policy and terms of service links

### 6. Review User Registration
Consider disabling public signup if this is for internal use:
```python
# In pages/login.py, comment out the Sign Up tab
# tab1, tab2 = st.tabs(["🔐 Login", "📝 Sign Up"])
tab1 = st.container()
with tab1:
    show_login_form()
```

### 7. Error Handling
- [ ] Review all error messages (don't expose sensitive info)
- [ ] Set up error logging
- [ ] Configure email notifications for errors

## Deployment Platform Setup

### 8. Streamlit Cloud (if using)
```bash
# Requirements
- GitHub repository (public or private)
- Streamlit Cloud account
- Add secrets via Streamlit Cloud UI (not .env file)
```

**Secrets Configuration in Streamlit Cloud:**
```toml
# .streamlit/secrets.toml (add via Streamlit Cloud UI)
[secrets]
AI_PROVIDER = "gemini"
GOOGLE_API_KEY = "your_production_key_here"
GEMINI_PARSING_MODEL = "gemini-2.5-flash"
GEMINI_EXPLANATION_MODEL = "gemini-2.5-flash"
```

### 9. Custom Server Deployment

**Requirements:**
```bash
pip install -r requirements.txt
```

**Environment Variables:**
```bash
export STREAMLIT_SERVER_PORT=8501
export STREAMLIT_SERVER_ADDRESS=0.0.0.0
export STREAMLIT_SERVER_HEADLESS=true
```

**Run with:**
```bash
streamlit run app.py --server.port 8501 --server.address 0.0.0.0
```

**Production Server (using systemd):**
```ini
# /etc/systemd/system/tpa-demo.service
[Unit]
Description=TPA Match Demo
After=network.target

[Service]
Type=simple
User=your_user
WorkingDirectory=/path/to/TPA Demo
Environment="PATH=/path/to/venv/bin"
ExecStart=/path/to/venv/bin/streamlit run app.py --server.port 8501
Restart=always

[Install]
WantedBy=multi-user.target
```

### 10. HTTPS Setup
- [ ] Use reverse proxy (nginx/caddy)
- [ ] Configure SSL certificate (Let's Encrypt)
- [ ] Enable HTTPS redirect
- [ ] Set secure cookie flags

**Example nginx config:**
```nginx
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl;
    server_name your-domain.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## Monitoring & Maintenance

### 11. Set Up Monitoring
- [ ] Application uptime monitoring
- [ ] Error rate tracking
- [ ] API usage/quota monitoring (for AI features)
- [ ] Database size monitoring

### 12. Backup Strategy
```bash
# Automated backup script
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
cp database/tpa_match_demo.db backups/tpa_match_demo_${DATE}.db

# Keep only last 30 days
find backups/ -name "*.db" -mtime +30 -delete
```

### 13. Update Documentation
- [ ] Update README with deployment instructions
- [ ] Document admin procedures
- [ ] Create user guide
- [ ] Document API integrations

## Pre-Launch Testing

### 14. Test All Features
- [ ] Login/logout functionality
- [ ] User registration (if enabled)
- [ ] Match request submission
- [ ] AI parsing (if enabled)
- [ ] Results viewing
- [ ] Vendor browsing
- [ ] Feedback submission

### 15. Security Testing
- [ ] SQL injection attempts
- [ ] XSS attempts
- [ ] Authentication bypass attempts
- [ ] Rate limiting (if implemented)

### 16. Performance Testing
- [ ] Load testing with multiple concurrent users
- [ ] Database query performance
- [ ] AI API response times
- [ ] Page load times

## Launch Day

### 17. Final Checks
- [ ] Demo accounts removed
- [ ] Admin account created
- [ ] SSL certificate valid
- [ ] Monitoring active
- [ ] Backup system running
- [ ] Error notifications working

### 18. Go Live
```bash
# 1. Pull latest code
git pull origin main

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run database migrations if any
python scripts/create_users_table.py

# 4. Remove demo users
python scripts/remove_demo_users.py

# 5. Start application
streamlit run app.py
```

### 19. Post-Launch Monitoring
- [ ] Monitor error logs for first 24 hours
- [ ] Check authentication is working
- [ ] Verify AI features are functioning
- [ ] Monitor API usage/costs
- [ ] Check database growth

## Ongoing Maintenance

### 20. Regular Tasks
- **Daily:** Check error logs
- **Weekly:** Review user activity, backup database
- **Monthly:** Update dependencies, security patches
- **Quarterly:** Review and rotate API keys

---

## Quick Command Reference

```bash
# Remove demo accounts
python scripts/remove_demo_users.py

# Create new admin user (use signup form in app)
# Or programmatically:
python -c "from scripts.auth import create_user; create_user('admin', 'admin@company.com', 'secure_password', 'Admin User', 'admin')"

# Backup database
cp database/tpa_match_demo.db database/backup_$(date +%Y%m%d).db

# Check active users
sqlite3 database/tpa_match_demo.db "SELECT username, email, role, last_login FROM users WHERE is_active = 1;"

# Deactivate user (don't delete)
sqlite3 database/tpa_match_demo.db "UPDATE users SET is_active = 0 WHERE username = 'username';"
```

---

**Remember:** This is a demo application. For production use with sensitive data, consider:
- Professional security audit
- Penetration testing
- Compliance review (GDPR, HIPAA, etc.)
- Legal review of terms and privacy policy
- Insurance/liability considerations
