# 🚀 QUICK START - Nigerian ALPR System

## ⚡ 30-Second Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the app
streamlit run alpr_system/ui/app.py

# 3. Open browser
# http://localhost:8501
```

## 📝 One-Minute Usage

1. **Upload** → Drag/drop image or video
2. **Preview** → See file immediately
3. **Detect** → Click "🔍 Detect Plate" button
4. **View** → See results with vehicle details
5. **Clear** → Click "🗑️ Clear" to reset

## ✅ Test the System

Try these plates in your images:

| Plate | Owner | Status |
|-------|-------|--------|
| KTS-123AB | Lawal Nasiru | ✅ Found |
| LAG-456CD | Adewale Johnson | ✅ Found |
| NEW-999XX | (any unknown) | ⚠️ Not found |
| ABC-1234X | (invalid format) | ❌ Invalid |

## 🎯 What You Get

✅ Clean Streamlit UI
✅ Nigerian plate format (AAA-123AA)
✅ 15 vehicle records
✅ Image & video support
✅ Professional result display
✅ Complete error handling

## 📚 Documentation

- **[RUN_GUIDE.md](RUN_GUIDE.md)** - Complete guide
- **[TESTING_REPORT.md](TESTING_REPORT.md)** - Test results
- **[IMPLEMENTATION_COMPLETE.md](IMPLEMENTATION_COMPLETE.md)** - Features

## 🆘 Troubleshooting

**Port already in use?**
```bash
streamlit run alpr_system/ui/app.py --server.port 8502
```

**Module not found?**
```bash
pip install -r requirements.txt
```

**Need to kill streamlit?**
```bash
pkill -f streamlit
```

## 💾 Key Files

```
alpr_system/
├── ui/app.py              ← Web interface
├── main.py                ← Detection pipeline
├── plate_validation.py    ← Format validation
└── vehicle_db.py          ← Vehicle records
```

---

**Status:** ✅ Ready to Use  
**Version:** 1.0  
**Date:** January 19, 2026
