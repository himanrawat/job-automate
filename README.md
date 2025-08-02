# Himanshu Rawat's Job Application Automation

🚀 **Automated job application system powered by Apify LinkedIn Jobs Scraper with intelligent prioritization and comprehensive tracking**

## ✨ Features

- **Professional Job Discovery**: Powered by Apify LinkedIn Jobs Scraper for reliable, large-scale job discovery
- **Intelligent Application**: Automated form filling with manual fallback
- **Smart Prioritization**: AI-powered job matching and priority scoring  
- **Comprehensive Tracking**: Google Sheets integration with CSV fallback
- **Document Generation**: Custom resumes and cover letters for each application
- **Global Reach**: Support for multiple countries and regions
- **Cost-Effective**: Efficient API usage with built-in rate limiting

## 🚨 Latest Updates & Major Changes

### ✅ Major Upgrade: Apify Integration
- 🔥 **NEW**: Integrated Apify LinkedIn Jobs Scraper for professional-grade job discovery
- ✅ **Removed**: Traditional LinkedIn and Naukri scrapers (replaced by Apify)
- ✅ **Enhanced**: Intelligent job filtering and priority scoring
- ✅ **Reliable**: No more bot detection issues or rate limiting problems
- ✅ **Scalable**: Discover thousands of jobs quickly and efficiently

### ✅ Previous Fixes
- ✅ **Google API Key Formatting** - Fixed "Incorrect padding" errors
- ✅ **ChromeDriver Auto-Management** - Automatic driver download and setup
- ✅ **Browser Compatibility** - Enhanced Chrome detection and configuration
- ✅ **CSV Fallback System** - Works even when Google Sheets quota exceeded
- ✅ **Error Handling** - Robust error handling for all components

### 🔧 Current Status
- **Apify LinkedIn Scraper**: ✅ Active and working
- **Google Credentials**: ✅ Working
- **Browser Setup**: ✅ Working (for applications only)
- **Google Sheets**: ✅ Working
- **Job Discovery**: ✅ Powered by Apify (reliable & scalable)

## 📦 Quick Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure API Keys
Update your `.env` file with required credentials:
```bash
# Required: Apify API Token
APIFY_API_TOKEN=your_apify_token_here

# Required: OpenAI API Key
OPENAI_API_KEY=your_openai_key_here

# Required: Google Service Account Credentials
GOOGLE_PROJECT_ID=your_project_id
GOOGLE_PRIVATE_KEY=your_private_key
# ... other Google credentials
```

### 3. Test Apify Integration
```bash
python test_apify_integration.py
```

### 4. Run Job Automation
```bash
python main.py
```

## 🔧 Configuration

### Google Drive API Setup
If you get Google Drive API errors:
1. Go to [Google Cloud Console](https://console.developers.google.com/apis/api/drive.googleapis.com/overview)
2. Select project: `job-automate-467805`
3. Enable Google Drive API and Google Sheets API

### Storage Quota Issues
If your Google Drive storage is full:
- The system automatically switches to CSV fallback mode
- Data is stored in `job_data/` folder as CSV files
- Export to Excel with: `python -c "from utils.csv_data_manager import CSVDataManager; CSVDataManager().export_to_excel('INDIA')"`

## 📊 Data Storage

### Google Sheets (Primary)
- **Spreadsheet**: "Himanshu Rawat - Job Applications Tracker"
- **Service Account**: `job-automate-sheet@job-automate-467805.iam.gserviceaccount.com`

### CSV Fallback (When Sheets Unavailable)
- **Location**: `job_data/`
- **Format**: `{REGION}_{YEAR}_{MONTH}.csv`
- **Export**: Automatic Excel export available

## 🎯 Usage

### Basic Job Search
```python
from main import HimanshuJobAutomator

automator = HimanshuJobAutomator()
automator.run_automation()
```

### Manual Data Export
```python
from utils.csv_data_manager import CSVDataManager

csv_manager = CSVDataManager()
# Export to Excel
csv_manager.export_to_excel('INDIA')
# List all data files
files = csv_manager.list_all_data_files()
```

## 🛠️ Troubleshooting

### Common Issues & Solutions

#### 1. Google Sheets Error (403)
**Error**: Google Drive API not enabled or storage quota exceeded
**Solution**:
- Enable APIs: [Google Drive](https://console.developers.google.com/apis/api/drive.googleapis.com) & [Google Sheets](https://console.developers.google.com/apis/api/sheets.googleapis.com)
- Free up Google Drive storage or upgrade plan
- System automatically uses CSV fallback

#### 2. Browser Setup (Optional)
**Note**: Browser automation is optional - core features work without it
**Error**: ChromeDriver issues
**Solution**: 
- Browser automation is only used for optional automated form filling
- Core features (Apify scraping, AI document generation, Google Sheets) work without browser
- If needed: Install latest Google Chrome and ensure it's in your system PATH

#### 3. Import Errors
**Error**: Module not found errors
**Solution**:
```bash
pip install -r requirements.txt
```

#### 4. Google Credentials Error
**Error**: "No key could be detected" or "Incorrect padding"
**Solution**:
- Check `.env` file exists with all required values
- Ensure private key has proper `\n` line breaks
- Validate project ID matches Google Cloud project

### Test Your Setup
```bash
python test_setup.py
```

## 📁 Project Structure

```
himanshu_job_automation/
├── main.py                 # Main application runner
├── test_setup.py          # Setup validation script
├── requirements.txt       # Python dependencies
├── .env                   # API keys and configuration
├── config/               # Configuration files
├── utils/                # Utility modules
│   ├── browser_setup.py   # Chrome browser management
│   ├── sheets_manager.py  # Google Sheets + CSV fallback
│   └── csv_data_manager.py # CSV data handling
├── scrapers/             # Job site scrapers
├── applications/         # Application automation
└── job_data/            # CSV data files (fallback)
```

## 🚀 Next Steps

1. **Immediate**: Test the fixed setup with `python test_setup.py`
2. **Short-term**: Clear Google Drive space to re-enable Sheets integration
3. **Medium-term**: Consider upgrading Google Drive storage plan
4. **Long-term**: Explore additional job portals and automation features

## 💡 Tips

- **Daily Limit**: System respects rate limits and daily application quotas
- **Data Backup**: CSV files serve as backup even when Sheets work
- **Regional Focus**: Configure regions in `config/job_preferences.py`
- **Customization**: Modify scraping patterns in `scrapers/` folder

## 📧 Support

For issues or questions:
1. Check this README's troubleshooting section
2. Run `python test_setup.py` for diagnostics
3. Review log files for detailed error information

---

**Last Updated**: August 2, 2025  
**Status**: Ready for use with CSV fallback enabled