# 🗳️ Meeting Poll App

A simple, web-based meeting poll application similar to Doodle.com. Create polls, share links, and find the perfect meeting time!

## ✨ Features

- ✅ Create meeting polls with multiple time slots
- ✅ Share unique poll links (no login required)
- ✅ Vote on availability (Yes/Maybe/No)
- ✅ Real-time results table
- ✅ Clean, responsive design
- ✅ Automatic link sharing
- ✅ SQLite database (portable)

## 🚀 Quick Start (Local)

### Option 1: Double-Click to Run
1. **Download all files** to a folder
2. **Double-click `run.py`** 
3. **Your browser will open automatically** at `http://localhost:5000`

### Option 2: Command Line
```bash
# Install Python dependencies
pip install -r requirements.txt

# Run the application
python app.py
```

## 📁 File Structure
```
meeting-poll-app/
├── app.py              # Main Flask application
├── run.py             # Simple launcher (double-click this!)
├── requirements.txt   # Python dependencies
├── README.md         # This file
├── polls.db          # SQLite database (created automatically)
└── templates/        # HTML templates (created automatically)
    ├── base.html
    ├── index.html
    └── poll_detail.html
```

## 🌐 Deploy to Render.com (Free)

### Step 1: Prepare Your Code
1. Create a free GitHub account if you don't have one
2. Create a new repository and upload all files
3. Make sure `requirements.txt` and `app.py` are in the root directory

### Step 2: Deploy on Render
1. Go to [render.com](https://render.com) and sign up
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Configure the deployment:
   - **Name**: `meeting-poll-app` (or your choice)
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
   - **Plan**: Free (for testing)

5. Click "Create Web Service"
6. Wait 2-3 minutes for deployment
7. Your app will be live at `https://your-app-name.onrender.com`

### Step 3: Configure for Production
Add these environment variables in Render dashboard:
- `FLASK_ENV` = `production`
- `SECRET_KEY` = `your-secret-key-here-change-this`

## 🎯 How to Use

### Creating a Poll
1. Visit your app homepage
2. Enter poll title and description
3. Add multiple time slot options
4. Click "Create Poll & Get Shareable Link"
5. Share the unique URL with participants

### Voting on a Poll
1. Open the poll link
2. Enter your name
3. Select Yes/Maybe/No for each time slot
4. Click "Submit My Availability"
5. View results immediately

### Viewing Results
- Results update automatically every 30 seconds
- See individual votes in a table format
- View summary counts for each time slot
- Identify the most popular meeting times

## 🛠️ Technical Details

- **Backend**: Python Flask
- **Frontend**: Bootstrap 5 + HTML/CSS/JavaScript
- **Database**: SQLite (file-based, portable)
- **No Authentication**: Simple name-based voting
- **Responsive**: Works on desktop and mobile

## 🔧 Customization

### Change App Name/Branding
Edit `templates/base.html`:
```html
<a class="navbar-brand" href="/">
    <i class="fas fa-calendar-check"></i> Your App Name
</a>
```

### Modify Colors
Edit the CSS in `templates/base.html`:
```css
.poll-header { 
    background: linear-gradient(135deg, #your-color 0%, #your-color2 100%); 
}
```

### Add Features
- Edit `app.py` for backend logic
- Modify templates for UI changes
- Add new routes for additional functionality

## 🐛 Troubleshooting

### Common Issues

**Port already in use:**
```bash
# Kill process on port 5000
lsof -ti:5000 | xargs kill
```

**Database locked:**
```bash
# Remove database file and restart
rm polls.db
python app.py
```

**Templates not found:**
- Make sure `templates/` folder exists
- Run `python app.py` to auto-create templates

**Render deployment fails:**
- Check `requirements.txt` is present
- Ensure `gunicorn` is in requirements
- Verify `app:app` in start command

## 📊 Database Schema

```sql
-- Polls table
CREATE TABLE polls (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Time slots for each poll
CREATE TABLE time_slots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    poll_id TEXT NOT NULL,
    slot_datetime TEXT NOT NULL,
    FOREIGN KEY (poll_id) REFERENCES polls (id)
);

-- Votes from participants
CREATE TABLE votes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    poll_id TEXT NOT NULL,
    voter_name TEXT NOT NULL,
    time_slot_id INTEGER NOT NULL,
    availability TEXT CHECK (availability IN ('yes', 'maybe', 'no')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (poll_id) REFERENCES polls (id),
    UNIQUE(poll_id, voter_name, time_slot_id)
);
```

## 🚀 Future Enhancements

Ideas for version 2.0:
- Email notifications
- Calendar integration
- Poll editing/deletion
- Admin dashboard
- Export to CSV
- Multiple poll formats
- User accounts (optional)
- Poll expiration dates
- Comments/notes feature

## 📝 License

Please do not modify this yet. Currently not open source yet.

## 🤝 Support

Having issues? 
1. Check the troubleshooting section
2. Ensure all files are in the same directory
3. Verify Python 3.7+ is installed
4. Make sure port 5000 is available

---

**Ready to find the perfect meeting time? Double-click `run.py` to get started! 🎉**
