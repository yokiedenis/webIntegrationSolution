# Quick Start Guide

## 🚀 Get Running in 5 Minutes
navigate to source code folders on terminal using [cd webIntegrationTests]
### Start Backend

```bash
cd server
npm install
npm start
```

Backend will be available at `http://localhost:5000`

### Start Frontend

In a new terminal:

```bash
cd client
npm install
npm run dev
```

Frontend will be available at `http://localhost:3000`

### Test the Chat

1. Open `http://localhost:3000` in your browser
2. Type a message like "How do I reset my password?"
3. See the agent respond!

## 📝 Example Messages to Try

- "What's your return policy?"
- "I forgot my password"
- "Where is my order?"
- "The app won't load"
- "I need a refund"

## 🔧 Troubleshooting

**Backend won't start?**
- Make sure port 5000 is free
- Check Node.js is installed: `node --version`

**Frontend showing errors?**
- Clear `node_modules`: `rm -rf node_modules && npm install`
- Check backend is running on port 5000

**Styles not loading?**
- Restart dev server: `npm run dev`

## 📚 Learn More

See [README.md](./README.md) for complete documentation.
