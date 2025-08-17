# 🚀 Streamlit Community Cloud Deployment Guide
## NLB Events Assistant MVP

This guide will walk you through deploying your NLB Events Assistant to Streamlit Community Cloud.

---

## 📋 **Prerequisites**

### **1. GitHub Account & Repository**
- ✅ GitHub account (free)
- ✅ Repository with your code (public or private)
- ✅ All code committed and pushed to GitHub

### **2. OpenAI API Key**
- ✅ Valid OpenAI API key with credits
- ✅ Access to GPT-3.5-turbo model
- ✅ Estimated cost: ~$0.01-0.03 per interaction

### **3. Project Structure Verification**
Your project should have this structure:
```
nlb_events_app/
├── main.py                    # Entry point
├── requirements.txt           # Dependencies
├── .gitignore                # Git ignore rules
├── data/                     # Event data
│   ├── nlb_events.jsonl
│   └── nlb-events.json
├── pages/                    # Streamlit pages
│   ├── 1_use_case_1.py
│   ├── 2_use_case_2.py
│   ├── 3_about_us.py
│   ├── 4_methodology.py
│   └── 5_database_browser.py
└── utils/                    # Core modules
    ├── __init__.py
    ├── llm_enhancer.py
    ├── rag_database.py
    ├── scraper.py
    └── security.py
```

---

## 🔧 **Step 1: Prepare Your Repository**

### **1.1 Create GitHub Repository**
```bash
# If not already done, create a new repository on GitHub
# Name: nlb-events-app (or your preferred name)
# Make it public (recommended for Streamlit Community Cloud)
```

### **1.2 Push Your Code**
```bash
# Navigate to your project directory
cd D:\dev\ai-bootcamp\nlb_events_app

# Initialize git (if not already done)
git init

# Add all files
git add .

# Commit changes
git commit -m "Initial commit: NLB Events Assistant MVP"

# Add remote repository (replace with your GitHub repo URL)
git remote add origin https://github.com/YOUR_USERNAME/nlb-events-app.git

# Push to GitHub
git push -u origin main
```

### **1.3 Verify Repository Structure**
Ensure these files are in your GitHub repository:
- ✅ `main.py`
- ✅ `requirements.txt`
- ✅ All files in `pages/` and `utils/` directories
- ✅ Data files in `data/` directory
- ❌ `.env` file (should NOT be committed - contains secrets)

---

## 🌐 **Step 2: Deploy to Streamlit Community Cloud**

### **2.1 Access Streamlit Community Cloud**
1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Sign in with your GitHub account
3. Click **"New app"**

### **2.2 Configure Your App**
Fill in the deployment form:

**Repository Settings:**
- **Repository**: `YOUR_USERNAME/nlb-events-app`
- **Branch**: `main`
- **Main file path**: `main.py`

**App Settings:**
- **App URL**: `nlb-events-app` (or your preferred name)
- **Description**: `NLB Events Assistant - AI-powered library event discovery`

### **2.3 Advanced Settings (Optional)**
Click **"Advanced settings"** and configure:
- **Python version**: `3.11` (recommended)
- **Requirements file**: `requirements.txt`

### **2.4 Deploy**
Click **"Deploy!"** and wait for the build process.

---

## 🔐 **Step 3: Configure Secrets**

### **3.1 Access App Settings**
1. Go to your deployed app URL
2. Click the hamburger menu (☰) in the top right
3. Select **"Settings"**

### **3.2 Add Secrets**
In the **"Secrets"** section, add your environment variables:

```toml
[secrets]
OPENAI_API_KEY = "sk-your-actual-openai-api-key-here"
LLM_MODEL = "gpt-3.5-turbo"
APP_PASSWORD = "nlbevents2024"
```

### **3.3 Save and Restart**
1. Click **"Save"**
2. Your app will automatically restart with the new secrets

---

## 🧪 **Step 4: Test Your Deployment**

### **4.1 Basic Functionality Test**
1. **Access your app**: Visit your Streamlit Community Cloud URL
2. **Password protection**: Enter the password (`nlbevents2024`)
3. **Navigation**: Test all pages load correctly
4. **Use Case 1**: Test event data processing
5. **Use Case 2**: Test Eventie chatbot functionality

### **4.2 API Integration Test**
1. **LLM Enhancement**: Process a few events in Use Case 1
2. **Chatbot**: Have a conversation with Eventie
3. **Error Handling**: Verify graceful error messages

### **4.3 Performance Test**
- **Load time**: Should be under 30 seconds
- **Response time**: LLM calls should complete in 2-3 seconds
- **Memory usage**: Should stay within Streamlit limits

---

## 🔧 **Step 5: Troubleshooting Common Issues**

### **5.1 Build Failures**
**Issue**: App fails to deploy
**Solutions**:
- Check `requirements.txt` has all dependencies
- Verify Python version compatibility
- Check for syntax errors in code

### **5.2 Import Errors**
**Issue**: Module not found errors
**Solutions**:
- Ensure all files are committed to GitHub
- Check file paths in imports
- Verify `utils/` directory structure

### **5.3 API Key Issues**
**Issue**: OpenAI API errors
**Solutions**:
- Verify API key is correct in secrets
- Check API key has sufficient credits
- Ensure API key has access to GPT-3.5-turbo

### **5.4 Data Loading Issues**
**Issue**: Events not loading
**Solutions**:
- Verify `data/` files are committed
- Check file paths in code
- Ensure JSON files are valid

---

## 📊 **Step 6: Monitor and Maintain**

### **6.1 Monitor Usage**
- **Streamlit Dashboard**: Check app performance
- **OpenAI Usage**: Monitor API costs
- **User Feedback**: Collect user experience data

### **6.2 Regular Maintenance**
- **Update Dependencies**: Keep packages current
- **Monitor Costs**: Track OpenAI API usage
- **Backup Data**: Regular data backups
- **Security Updates**: Keep secrets secure

### **6.3 Scaling Considerations**
- **User Load**: Monitor concurrent users
- **API Limits**: Watch OpenAI rate limits
- **Storage**: Monitor data storage usage

---

## 🎯 **Step 7: Final Checklist**

### **✅ Pre-Deployment**
- [ ] All code committed to GitHub
- [ ] Repository is public (or private with proper access)
- [ ] `requirements.txt` is complete and accurate
- [ ] `.env` file is NOT committed (contains secrets)
- [ ] All data files are included

### **✅ Deployment**
- [ ] App deployed successfully to Streamlit Community Cloud
- [ ] Secrets configured correctly
- [ ] App URL is accessible
- [ ] Password protection working

### **✅ Post-Deployment**
- [ ] All pages load correctly
- [ ] Use Case 1 (Data Processing) works
- [ ] Use Case 2 (Eventie Chatbot) works
- [ ] LLM integration functioning
- [ ] Error handling working properly
- [ ] Performance is acceptable

### **✅ Documentation**
- [ ] Update README.md with deployment info
- [ ] Document any custom configurations
- [ ] Share app URL with stakeholders

---

## 🔗 **Useful Links**

- **Streamlit Community Cloud**: [share.streamlit.io](https://share.streamlit.io)
- **GitHub**: [github.com](https://github.com)
- **OpenAI API**: [platform.openai.com](https://platform.openai.com)
- **Streamlit Documentation**: [docs.streamlit.io](https://docs.streamlit.io)

---

## 📞 **Support**

If you encounter issues:
1. Check Streamlit Community Cloud logs
2. Review GitHub repository for errors
3. Test locally first
4. Consult Streamlit documentation
5. Check OpenAI API status

---

**🎉 Congratulations!** Your NLB Events Assistant is now deployed and ready for use!
