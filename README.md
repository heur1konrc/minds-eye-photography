# Mind's Eye Photography v2.0

🎉 **Fresh Start with Working Backup System!**

## What's New in v2.0

- ✅ **Clean Flask application structure**
- ✅ **Working backup system with downloads**
- ✅ **Proper database models**
- ✅ **No deployment nightmares**
- ✅ **Built for reliability**

## Quick Start

1. **Deploy to Railway** - Connect this repo to Railway
2. **Test backup system** - Go to `/admin/backup` and test backup creation
3. **Restore your data** - Use your backup file to restore portfolio
4. **Upload images** - With confidence knowing backups work!

## Features

### 🔧 Backup System
- Custom filename support
- Direct download functionality
- Comprehensive tar.gz backups
- Database + images + settings

### 📸 Portfolio Management
- Image upload with EXIF data
- Category organization
- Featured image selection
- Background image management

### 🎯 Admin Interface
- Clean, modern design
- Easy navigation
- Status monitoring
- Contact form management

## File Structure

```
minds-eye-v2/
├── src/
│   ├── models/
│   │   └── database.py      # Database models
│   ├── routes/
│   │   ├── admin.py         # Admin interface & backup system
│   │   └── api.py           # API endpoints
│   ├── static/
│   │   └── assets/          # Image uploads
│   ├── templates/
│   │   └── index.html       # Homepage
│   └── main.py              # Flask application
├── database/                # SQLite database
├── requirements.txt         # Python dependencies
├── Procfile                 # Railway deployment
└── README.md               # This file
```

## Environment Variables

- `PORT` - Application port (set by Railway)
- `SECRET_KEY` - Flask secret key (optional, has default)

## Deployment

This app is designed for Railway deployment:

1. Connect GitHub repo to Railway
2. Railway auto-detects Python and uses Procfile
3. Database is created automatically
4. Ready to use!

## Testing the Backup System

**IMPORTANT:** Test the backup system FIRST before adding any data!

1. Go to `/admin/backup`
2. Create a test backup
3. Verify download works
4. Check backup file contents

## Restoring Data

Once backup system is confirmed working:

1. Use your backup file from the old system
2. Extract and restore database
3. Upload images to `src/static/assets/`
4. Verify everything works

## Version History

- **v1.x** - Original system (had deployment issues)
- **v2.0** - Fresh start with working backup system

---

**Built with determination and lessons learned from v1.x deployment nightmares!** 🚀
