import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import random
import math
from datetime import datetime, timedelta
import json

# Emotion-based color palettes
EMOTION_PALETTES = {
    "😊 Happy": [(1.0, 0.9, 0.2), (1.0, 0.7, 0.3), (1.0, 0.5, 0.6), (0.9, 0.9, 0.5), (1.0, 0.8, 0.4)],
    "😢 Sad": [(0.3, 0.4, 0.6), (0.4, 0.5, 0.7), (0.5, 0.6, 0.8), (0.2, 0.3, 0.5), (0.6, 0.7, 0.9)],
    "😠 Angry": [(0.9, 0.2, 0.2), (0.8, 0.3, 0.1), (1.0, 0.4, 0.2), (0.7, 0.1, 0.1), (0.9, 0.5, 0.3)],
    "😌 Calm": [(0.6, 0.8, 0.7), (0.5, 0.9, 0.8), (0.7, 0.9, 0.9), (0.4, 0.7, 0.6), (0.8, 0.95, 0.9)],
    "😰 Anxious": [(0.6, 0.5, 0.7), (0.5, 0.4, 0.6), (0.7, 0.6, 0.8), (0.4, 0.3, 0.5), (0.8, 0.7, 0.9)],
    "😍 Excited": [(1.0, 0.3, 0.6), (0.9, 0.4, 0.8), (1.0, 0.5, 0.5), (0.9, 0.2, 0.5), (1.0, 0.6, 0.7)],
    "😴 Tired": [(0.5, 0.5, 0.5), (0.6, 0.6, 0.6), (0.4, 0.4, 0.4), (0.7, 0.7, 0.7), (0.55, 0.55, 0.55)],
    "💖 Loved": [(1.0, 0.7, 0.8), (0.9, 0.6, 0.7), (1.0, 0.8, 0.9), (0.9, 0.5, 0.6), (1.0, 0.75, 0.85)]
}

def blob(center=(0.5, 0.5), r=0.3, points=200, wobble=0.15):
    """Generate a wobbly blob shape"""
    angles = np.linspace(0, 2 * math.pi, points, endpoint=False)
    radii = r * (1 + wobble * (np.random.rand(points) - 0.5))
    x = center[0] + radii * np.cos(angles)
    y = center[1] + radii * np.sin(angles)
    return x, y

def generate_emotion_art(emotion, date_str, note="", intensity=5, seed=None):
    """Generate abstract art based on emotion"""
    if seed is None:
        seed = hash(date_str) % 10000
    
    random.seed(seed)
    np.random.seed(seed)
    
    fig, ax = plt.subplots(figsize=(6, 8))
    ax.axis('off')
    ax.set_facecolor((0.98, 0.98, 0.97))
    
    palette = EMOTION_PALETTES.get(emotion, EMOTION_PALETTES["😌 Calm"])
    
    # Intensity affects number of layers and wobble
    n_layers = int(5 + intensity * 1.5)
    wobble = 0.1 + (intensity / 10) * 0.3
    
    for _ in range(n_layers):
        cx, cy = random.random(), random.random()
        rr = random.uniform(0.15, 0.45)
        x, y = blob((cx, cy), r=rr, wobble=wobble)
        color = random.choice(palette)
        alpha = random.uniform(0.3, 0.6)
        ax.fill(x, y, color=color, alpha=alpha, edgecolor='none')
    
    # Add date and emotion text
    ax.text(0.05, 0.96, date_str, transform=ax.transAxes, 
            fontsize=14, weight='bold', color='#333')
    ax.text(0.05, 0.92, emotion, transform=ax.transAxes, 
            fontsize=16, weight='bold')
    
    if note:
        # Wrap long text
        wrapped_note = note[:50] + "..." if len(note) > 50 else note
        ax.text(0.05, 0.04, f'"{wrapped_note}"', transform=ax.transAxes, 
                fontsize=9, style='italic', color='#555')
    
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    
    return fig

def generate_weekly_art(entries):
    """Generate a combined art piece from multiple entries"""
    if not entries:
        return None
    
    fig, ax = plt.subplots(figsize=(10, 8))
    ax.axis('off')
    ax.set_facecolor((0.98, 0.98, 0.97))
    
    # Combine all palettes from the week
    all_colors = []
    for entry in entries:
        emotion = entry.get('emotion', '😌 Calm')
        palette = EMOTION_PALETTES.get(emotion, EMOTION_PALETTES["😌 Calm"])
        all_colors.extend(palette)
    
    random.seed(42)
    np.random.seed(42)
    
    # Create layers based on number of entries
    n_layers = len(entries) * 3
    
    for _ in range(n_layers):
        cx, cy = random.random(), random.random()
        rr = random.uniform(0.1, 0.3)
        x, y = blob((cx, cy), r=rr, wobble=0.2)
        color = random.choice(all_colors)
        alpha = random.uniform(0.2, 0.5)
        ax.fill(x, y, color=color, alpha=alpha, edgecolor='none')
    
    ax.text(0.5, 0.95, "My Weekly Emotions", transform=ax.transAxes,
            fontsize=18, weight='bold', ha='center')
    
    # Show emotion summary
    emotion_counts = {}
    for entry in entries:
        emotion = entry.get('emotion', '😌 Calm')
        emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
    
    summary = " • ".join([f"{e.split()[0]} {c}" for e, c in emotion_counts.items()])
    ax.text(0.5, 0.05, summary, transform=ax.transAxes,
            fontsize=10, ha='center', color='#555')
    
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    
    return fig

# Streamlit App
st.set_page_config(page_title="Emotion Color Diary", page_icon="🎨", layout="wide")

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        margin-bottom: 1rem;
        background: linear-gradient(90deg, #FF6B6B, #4ECDC4, #45B7D1);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .subtitle {
        text-align: center;
        color: #666;
        font-size: 1.2rem;
        margin-bottom: 2rem;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-header">🎨 Emotion Color Diary</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Transform your feelings into beautiful abstract art</div>', unsafe_allow_html=True)

# Initialize session state for storage
if 'entries' not in st.session_state:
    st.session_state.entries = {}

# Tabs
tab1, tab2, tab3 = st.tabs(["✍️ New Entry", "📅 Calendar View", "📊 Weekly Summary"])

with tab1:
    st.header("Create Today's Emotion Art")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("How are you feeling?")
        
        selected_date = st.date_input("Date", datetime.now())
        date_str = selected_date.strftime("%Y-%m-%d")
        
        emotion = st.selectbox("Select your emotion", list(EMOTION_PALETTES.keys()))
        
        intensity = st.slider("Emotion Intensity", 1, 10, 5,
                             help="How strong is this feeling?")
        
        note = st.text_area("Write a note (optional)", 
                           placeholder="What happened today?",
                           max_chars=200)
        
        if st.button("🎨 Generate Art", use_container_width=True, type="primary"):
            # Save entry
            st.session_state.entries[date_str] = {
                'emotion': emotion,
                'intensity': intensity,
                'note': note,
                'timestamp': datetime.now().isoformat()
            }
            st.success("Entry saved! ✨")
            st.rerun()
    
    with col2:
        st.subheader("Your Emotion Art")
        
        # Check if there's an entry for selected date
        if date_str in st.session_state.entries:
            entry = st.session_state.entries[date_str]
            fig = generate_emotion_art(
                entry['emotion'], 
                date_str, 
                entry['note'], 
                entry['intensity']
            )
        else:
            # Generate preview with current selections
            fig = generate_emotion_art(emotion, date_str, note, intensity)
        
        st.pyplot(fig)
        plt.close(fig)

with tab2:
    st.header("Your Emotion Calendar")
    
    if st.session_state.entries:
        # Get last 7 days
        today = datetime.now()
        dates = [(today - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(6, -1, -1)]
        
        cols = st.columns(7)
        for i, date in enumerate(dates):
            with cols[i]:
                day_name = datetime.strptime(date, "%Y-%m-%d").strftime("%a")
                st.markdown(f"**{day_name}**")
                st.markdown(f"<small>{date[5:]}</small>", unsafe_allow_html=True)
                
                if date in st.session_state.entries:
                    entry = st.session_state.entries[date]
                    emotion_icon = entry['emotion'].split()[0]
                    st.markdown(f"<div style='font-size: 3rem; text-align: center;'>{emotion_icon}</div>", 
                               unsafe_allow_html=True)
                    
                    if st.button("View", key=f"view_{date}", use_container_width=True):
                        st.session_state.view_date = date
                else:
                    st.markdown("<div style='font-size: 2rem; text-align: center; color: #ddd;'>—</div>", 
                               unsafe_allow_html=True)
        
        # Show selected date's art
        if 'view_date' in st.session_state and st.session_state.view_date in st.session_state.entries:
            st.markdown("---")
            entry = st.session_state.entries[st.session_state.view_date]
            
            col1, col2 = st.columns([1, 1])
            with col1:
                st.subheader(f"📅 {st.session_state.view_date}")
                st.write(f"**Emotion:** {entry['emotion']}")
                st.write(f"**Intensity:** {entry['intensity']}/10")
                if entry['note']:
                    st.write(f"**Note:** {entry['note']}")
            
            with col2:
                fig = generate_emotion_art(
                    entry['emotion'],
                    st.session_state.view_date,
                    entry['note'],
                    entry['intensity']
                )
                st.pyplot(fig)
                plt.close(fig)
    else:
        st.info("No entries yet. Create your first emotion art in the 'New Entry' tab! 🎨")

with tab3:
    st.header("Weekly Emotion Summary")
    
    if st.session_state.entries:
        # Get entries from last 7 days
        today = datetime.now()
        week_entries = []
        for i in range(7):
            date = (today - timedelta(days=i)).strftime("%Y-%m-%d")
            if date in st.session_state.entries:
                entry = st.session_state.entries[date].copy()
                entry['date'] = date
                week_entries.append(entry)
        
        if week_entries:
            col1, col2 = st.columns([1, 2])
            
            with col1:
                st.subheader("This Week's Emotions")
                for entry in reversed(week_entries):
                    st.write(f"**{entry['date']}**: {entry['emotion']}")
                
                st.markdown("---")
                st.metric("Total Entries", len(week_entries))
                
                # Most common emotion
                emotions = [e['emotion'] for e in week_entries]
                most_common = max(set(emotions), key=emotions.count)
                st.write(f"**Most frequent:** {most_common}")
            
            with col2:
                st.subheader("Combined Weekly Art")
                fig = generate_weekly_art(week_entries)
                if fig:
                    st.pyplot(fig)
                    plt.close(fig)
        else:
            st.info("No entries this week yet!")
    else:
        st.info("Create some entries to see your weekly summary! 🎨")

# Sidebar
st.sidebar.header("About")
st.sidebar.info(
    """
    **Emotion Color Diary** helps you visualize your feelings through generative art.
    
    Each emotion has its own color palette and pattern style:
    - 😊 Happy: Warm yellows and oranges
    - 😢 Sad: Cool blues
    - 😠 Angry: Bold reds
    - 😌 Calm: Peaceful greens
    - And more...
    
    Track your emotional journey and see patterns emerge!
    """
)

st.sidebar.markdown("---")
st.sidebar.markdown(f"**Total Entries:** {len(st.session_state.entries)}")

if st.sidebar.button("🗑️ Clear All Data"):
    st.session_state.entries = {}
    st.rerun()
