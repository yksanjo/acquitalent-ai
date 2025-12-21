# Screenshot Guide

## Required Screenshots

To complete the README, capture the following screenshots:

### 1. Dashboard Full View (`dashboard-full.png`)
- Capture the entire dashboard showing:
  - Header with "AcquiTalent AI" branding
  - Statistics cards (Total Candidates, Avg Openness Score)
  - Candidates table with sample data
- Dimensions: 1920x1080 or similar
- Format: PNG

### 2. Dashboard Overview (`dashboard-screenshot.png`)
- Main dashboard view (can be same as above or cropped)
- Shows the clean, modern UI

### 3. Candidates Table (`candidates-table.png`)
- Close-up of the candidates table
- Shows multiple candidates with scores
- Highlights the score visualization (progress bars)

### 4. Signal Fusion Results (`signal-fusion-results.png`)
- Shows the results after running signal fusion
- Displays candidate cards or table with scores
- Shows the "Found X candidates" message

## How to Capture

1. **Start the application**:
   ```bash
   # Terminal 1: Backend
   python main.py
   
   # Terminal 2: Frontend
   cd frontend
   npm run dev
   ```

2. **Open browser**: Navigate to `http://localhost:3000`

3. **Run Signal Fusion**: Click "Run Signal Fusion" button to generate sample data

4. **Capture screenshots**:
   - Use browser dev tools (Cmd+Shift+P → "Capture screenshot")
   - Or use a tool like CleanShot (Mac) or ShareX (Windows)
   - Save to `docs/` directory

5. **Update README**: Replace placeholder paths with actual screenshot paths

## UI Elements to Highlight

- Clean, modern design
- Score visualization (progress bars)
- Statistics cards
- Responsive table layout
- Professional color scheme

