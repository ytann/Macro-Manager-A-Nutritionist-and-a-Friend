# Plan B: Hybrid Lab-Journal UI Implementation

This plan evolves the "Notebook" concept into a "Hybrid Lab-Journal," blending the intimacy of a personal diary with the authority of a clinical medical record.

## 🎯 Objective
Establish a "Trust-based" visual hierarchy. Use analog elements for user-driven data (logs/notes) and high-precision digital elements for clinical AI insights.

## 🛠️ Implementation Steps

### 1. Visual Foundation (The "Base")
- **Background**: Retain the grid-paper background from `frontend_REF.py`.
- **Biophilic Palette**: Implement a new color scheme:
    - **Background**: Soft Cream (`#FDFBF7`)
    - **Primary**: Sage Green (`#8DAA91`)
    - **Accents**: Deep Slate (`#2F3E46`) and Muted Gold (`#C5A059`)
- **Typographic Split**:
    - **Analog (Courier Prime)**: Used for User Logs, Bio-text, and Sovereign Memory.
    - **Digital (Inter/System Sans)**: Used for Clinical Copilot responses, Macro HUD values, and Guardrail alerts.

### 2. High-Precision Components
- **The "Stamped" HUD**:
    - Modify the SVG rings to look like "Digital Stamps" on the paper.
    - Use high-contrast, clean Sans-serif fonts for the numbers to signal precision.
- **"Clinical Insert" Cards**:
    - Instead of standard text, the Clinical Copilot's responses will be rendered in "Insert" boxes (soft beige background, slight shadow, border-left accent) to look like medical clippings pinned to the page.
- **The "Insulin Gauge"**:
    - Style the weekly buffer bars as "precision sliders" with clear digital markers.

### 3. Feature Integration (The "Intelligence" Layer)
- **Clinical Copilot**: Port `/planner` interaction; output formatted as a "Clinical Insert."
- **Vision Logging**: Port `send_vision_log` into a "Visual Evidence" tab.
- **Voice Trigger**: Implement the `_MIC_HTML` trigger as a "Quick Note" button.
- **Sovereign Memory**: Implement as a "Field Notes" dialog.

### 4. UX Flow
- **Onboarding**: A guided "Intake Form" $\rightarrow$ "Baseline Calibration."
- **Dashboard**: A chronological "Lab Log" where daily entries are mixed with AI-driven "Clinical Observations."

## 📈 Success Criteria
- Successful visual distinction between "User Input" and "Clinical Truth."
- High readability across both monospace and sans-serif fonts.
- A "Premium" feel that balances emotional intimacy with medical authority.
