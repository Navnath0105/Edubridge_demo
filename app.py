import streamlit as st
import joblib
import google.generativeai as genai
import plotly.express as px
import pandas as pd
import time

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="EduBridge | AI Career Counselor",
    page_icon="🎓",
    layout="centered",
    initial_sidebar_state="auto"
)

# --- INITIALIZE SESSION STATES ---
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'username' not in st.session_state:
    st.session_state['username'] = ''
if 'theme' not in st.session_state:
    st.session_state['theme'] = 'dark' # Changed default to dark based on your screenshots
if 'user_db' not in st.session_state:
    # Adding the specific demo accounts
    st.session_state['user_db'] = {
        'panchalnavnath0105@gmail.com': 'Admin@123', 
        'student': 'student123'
    }

# --- DYNAMIC THEME SETTINGS ---
if st.session_state['theme'] == 'light':
    bg_color = "#F4F4FA"
    card_color = "#FFFFFF"
    text_color = "#111827"
    text_muted = "#64748B"
    border_color = "#E2E8F0"
else:
    bg_color = "#0F172A"
    card_color = "#1E293B"
    text_color = "#F8FAFC"
    text_muted = "#94A3B8"
    border_color = "#334155"

# --- GLOBAL CSS INJECTION ---
global_css = f"""
<style>
    /* Base App Theme */
    .stApp {{
        background-color: {bg_color} !important; 
    }}
    

    .block-container {{
        padding-top: 3rem !important; 
        padding-bottom: 6rem !important; /* Extra padding for chatbot */
    }}
    
    /* Force Sidebar to strictly follow our custom theme */
    [data-testid="stSidebar"] {{
        background-color: {card_color} !important;
    }}
    [data-testid="stSidebar"] p, 
    [data-testid="stSidebar"] span, 
    [data-testid="stSidebar"] .stRadio label p {{
        color: {text_color} !important;
    }}
    
    /* Typography Overrides */
    p, h1, h2, h3, h4, h5, h6, label, li {{
        color: {text_color} !important;
    }}
    
    /* Modern Cards (Tabs & Forms) */
    [data-testid="stTabs"], [data-testid="stForm"], .custom-card {{
        background-color: {card_color} !important;
        padding: 2.5rem !important;
        border-radius: 12px !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05) !important;
        border: 1px solid {border_color} !important;
    }}
    
    /* Remove redundant inner form borders */
    [data-testid="stTabs"] [data-testid="stForm"] {{
        padding: 0 !important;
        border: none !important;
        box-shadow: none !important;
    }}
    
    /* =========================================
       AGGRESSIVE INPUT FIELD OVERRIDES 
       ========================================= */
       
    /* Outer Wrapper */
    div[data-baseweb="base-input"], div[data-baseweb="select"] > div {{
        background-color: {card_color} !important;
        border: 1px solid {border_color} !important;
        border-radius: 6px !important;
    }}
    
    /* Inner Wrapper */
    div[data-baseweb="input"] {{
        background-color: transparent !important;
    }}
    
    /* Text and Select Box content */
    .stTextInput input, div[data-baseweb="select"] * {{
        color: {text_color} !important;
        -webkit-text-fill-color: {text_color} !important; 
    }}
    
    /* Password Eye Icon Box */
    [data-testid="stTextInput"] div[data-baseweb="input"] > div:last-child {{
        background-color: transparent !important;
    }}
    [data-testid="stTextInput"] div[data-baseweb="input"] > div:last-child * {{
        color: {text_muted} !important;
        -webkit-text-fill-color: {text_muted} !important; 
    }}
    
    /* Fix browser autofill background bleed */
    input:-webkit-autofill {{
        -webkit-box-shadow: 0 0 0 30px {card_color} inset !important;
        transition: background-color 5000s ease-in-out 0s;
    }}

    /* =========================================
       DROPDOWN MENU / POPOVER FIXES (From Previous Fix)
       ========================================= */
       
    div[data-baseweb="popover"], div[data-baseweb="popover"] > div {{
        background-color: {card_color} !important;
    }}
    
    ul[data-baseweb="menu"] {{
        background-color: {card_color} !important;
        border: 1px solid {border_color} !important;
        border-radius: 6px !important;
    }}
    
    li[role="option"] {{
        background-color: {card_color} !important;
        color: {text_color} !important;
    }}
    
    li[role="option"]:hover, li[role="option"][aria-selected="true"] {{
        background-color: {bg_color} !important;
    }}
    
    li[role="option"] span, li[role="option"] * {{
        color: {text_color} !important;
        -webkit-text-fill-color: {text_color} !important; 
    }}
    
    /* =========================================
       BUTTON STYLING FIXES
       ========================================= */
       
    /* Primary Gradient Button */
    [data-testid="stFormSubmitButton"] button, .stButton button[kind="primary"] {{
        background: linear-gradient(90deg, #2178d1 0%, #874ee4 100%) !important;
        color: white !important;
        border-radius: 6px !important;
        border: none !important;
        padding: 10px !important;
        font-weight: bold !important;
        -webkit-text-fill-color: white !important;
    }}
    [data-testid="stFormSubmitButton"] button:hover, .stButton button[kind="primary"]:hover {{
        opacity: 0.9 !important;
    }}
    
    /* Secondary Buttons (Sidebar Toggles, Logout) */
    .stButton button[kind="secondary"] {{
        background-color: transparent !important;
        color: {text_color} !important;
        border: 1px solid {border_color} !important;
        border-radius: 6px !important;
        -webkit-text-fill-color: {text_color} !important;
    }}
    .stButton button[kind="secondary"]:hover {{
        border-color: #874ee4 !important;
        color: #874ee4 !important;
        -webkit-text-fill-color: #874ee4 !important;
    }}
    
    /* =========================================
       CHATBOT UI FIXES
       ========================================= */
       
    [data-testid="stBottomBlockContainer"] {{
        background-color: {bg_color} !important;
    }}
    
    [data-testid="stChatInput"] {{
        background-color: {card_color} !important;
        border: 1px solid {border_color} !important;
        border-radius: 8px !important;
    }}
    
    [data-testid="stChatInput"] textarea {{
        color: {text_color} !important;
        -webkit-text-fill-color: {text_color} !important;
        background-color: transparent !important;
    }}
    
    [data-testid="stChatInput"] button svg {{
        fill: {text_color} !important;
    }}
    
    /* Tab Headers */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 20px;
        justify-content: center;
        margin-bottom: 20px;
    }}
    .stTabs [data-baseweb="tab"] p {{
        color: {text_muted} !important; 
        font-weight: 500 !important;
        font-size: 16px !important;
    }}
    .stTabs [aria-selected="true"] p {{
        color: #874ee4 !important; 
        font-weight: bold !important;
    }}
    .stTabs [aria-selected="true"] {{
        border-bottom: 3px solid #874ee4 !important;
    }}
</style>
"""
st.markdown(global_css, unsafe_allow_html=True)


# =====================================================================
# AUTHENTICATION PAGE (LOGIN & REGISTER)
# =====================================================================
if not st.session_state['logged_in']:
    
    spacer_left, main_content, spacer_right = st.columns([1, 2.5, 1])
    
    with main_content:
        tab_login, tab_register = st.tabs(["Sign In", "Create Account"])
        
        # --- LOGIN TAB ---
        with tab_login:
            with st.form("modern_login_form", clear_on_submit=False):
                st.markdown(f"""
                <div style='display: flex; flex-direction: column; align-items: center; margin-bottom: 20px;'>
                    <div style='background: linear-gradient(135deg, #2178d1, #874ee4); width: 60px; height: 60px; border-radius: 12px; display: flex; justify-content: center; align-items: center; color: white; font-size: 24px; font-weight: bold; margin-bottom: 15px;'>
                        EB
                    </div>
                    <h2 style='margin: 0; font-size: 28px;'>Welcome Back</h2>
                    <p style='margin: 5px 0 0 0; color: {text_muted}; font-size: 14px;'>Sign in to your account</p>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown(f"""
                <div style='background-color: rgba(33, 120, 209, 0.1); border: 1px solid #2178d1; border-radius: 6px; padding: 15px; margin-bottom: 20px;'>
                    <div style='color: #2178d1; font-size: 14px; font-weight: bold; margin-bottom: 8px;'>ⓘ Demo Accounts:</div>
                    <div style='color: {text_color}; font-size: 13px; line-height: 1.6;'>
                        <b>Admin:</b> panchalnavnath0105@gmail.com<br>
                        <b>Password:</b> Admin@123<br>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                username = st.text_input("Email Address", placeholder="Enter your email")
                password = st.text_input("Password", placeholder="Enter your password", type="password")
                
                st.markdown("<div style='text-align: right; font-size: 13px; color: #2178d1; margin-bottom: 10px; cursor: pointer;'>Forgot your password?</div>", unsafe_allow_html=True)
                submit_login = st.form_submit_button("Sign In", use_container_width=True)
                
                if submit_login:
                    clean_username = username.strip()
                    clean_password = password.strip()
                    if clean_username in st.session_state['user_db'] and st.session_state['user_db'][clean_username] == clean_password:
                        st.session_state['logged_in'] = True
                        st.session_state['username'] = clean_username
                        st.rerun()
                    else:
                        st.error("⚠️ Invalid email or password.")
                        
        # --- REGISTRATION TAB ---
        with tab_register:
            with st.form("modern_register_form", clear_on_submit=False):
                st.markdown(f"""
                <div style='background-color: rgba(255, 165, 0, 0.1); border: 1px solid #FFA500; border-radius: 6px; padding: 12px; margin-bottom: 25px; display: flex; align-items: flex-start; gap: 10px;'>
                    <div style='color: #FFA500; font-size: 16px;'>ⓘ</div>
                    <div style='color: {text_color}; font-size: 13px; line-height: 1.5;'>
                        <b>Note:</b> Fill details to register. You will be automatically logged in upon success.
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                new_fullname = st.text_input("Full Name", placeholder="Enter your full name")
                new_email = st.text_input("Email Address", placeholder="Enter your email")
                new_password = st.text_input("Password", placeholder="Create a password", type="password")
                confirm_password = st.text_input("Confirm Password", placeholder="Confirm your password", type="password")
                
                submit_register = st.form_submit_button("Create Account", use_container_width=True)
                
                if submit_register:
                    clean_new_email = new_email.strip()
                    clean_new_password = new_password.strip()
                    
                    if clean_new_email in st.session_state['user_db']:
                        st.error("⚠️ Email already registered. Please Sign In.")
                    elif not clean_new_email or not clean_new_password:
                        st.error("⚠️ Email and Password cannot be empty.")
                    elif clean_new_password != confirm_password.strip():
                        st.error("⚠️ Passwords do not match.")
                    else:
                        st.session_state['user_db'][clean_new_email] = clean_new_password
                        st.session_state['logged_in'] = True
                        st.session_state['username'] = clean_new_email
                        st.success("✅ Account created successfully! Logging you in...")
                        time.sleep(1)
                        st.rerun()

    st.stop()


# --- SIDEBAR NAVIGATION & THEME TOGGLE ---
display_name = st.session_state['username'].split('@')[0]

st.sidebar.markdown(f"""
    <div style="text-align: center; margin-bottom: 20px;">
        <div style='background: linear-gradient(135deg, #2178d1, #874ee4); width: 50px; height: 50px; border-radius: 10px; display: inline-flex; justify-content: center; align-items: center; color: white; font-size: 20px; font-weight: bold;'>
            EB
        </div>
        <h3 style='margin-bottom: 0px;'>Welcome,</h3>
        <h4 style='color: #874ee4; margin-top: 0px; word-wrap: break-word;'>{display_name}!</h4>
    </div>
""", unsafe_allow_html=True)

# Theme Toggle Button
theme_icon = "🌙 Dark Mode" if st.session_state['theme'] == 'light' else "☀️ Light Mode"
if st.sidebar.button(theme_icon, use_container_width=True, type="secondary"):
    st.session_state['theme'] = 'dark' if st.session_state['theme'] == 'light' else 'light'
    st.rerun()
    
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Navigation Menu",
    ["Career Recommendation", "Skill Gap Analysis", "AI Chatbot", "Admin Panel", "Student Dashboard"]
)

st.sidebar.markdown("---")

if st.sidebar.button("🚪 Logout", use_container_width=True, type="secondary"):
    st.session_state['logged_in'] = False
    st.session_state['username'] = ''
    st.rerun()
    

# --- ROUTING LOGIC ---

if page == "Career Recommendation":
    
    st.markdown("""
    <div style='text-align: center; padding-bottom: 25px;'>
        <h1 style='font-size: 2.5rem; font-weight: 800; margin-bottom: 0;'>
            <span style='background: linear-gradient(90deg, #2178d1, #874ee4); -webkit-background-clip: text; -webkit-text-fill-color: transparent;'>🎯 AI</span> Career Recommendation
        </h1>
        <p style='font-size: 1.1rem; margin-top: 10px;'>Select your background and interests to let the AI find your perfect career path.</p>
    </div>
    """, unsafe_allow_html=True)

    try:
        model = joblib.load('models/career_model.pkl')
        encoders = joblib.load('models/encoders.pkl')

        with st.form("career_form"):
            st.markdown(f"<h3 style='margin-top: 0px; margin-bottom: 5px;'>Student Profile</h3>", unsafe_allow_html=True)
            st.markdown(f"<hr style='margin: 0px 0px 20px 0px; border: 1px solid {border_color};'>", unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            with col1:
                degree = st.selectbox("🎓 Select your Degree", encoders['Degree'].classes_)
            with col2:
                skill = st.selectbox("💻 Select your Primary Skill", encoders['Primary_Skill'].classes_)
            
            interest = st.selectbox("❤️ Select your Main Interest", encoders['Interest'].classes_)
            
            st.markdown("<br>", unsafe_allow_html=True)
            submit_button = st.form_submit_button("Predict My Career", use_container_width=True)

        if submit_button:
            deg_encoded = encoders['Degree'].transform([degree])[0]
            skill_encoded = encoders['Primary_Skill'].transform([skill])[0]
            int_encoded = encoders['Interest'].transform([interest])[0]

            prediction = model.predict([[deg_encoded, skill_encoded, int_encoded]])
            
            st.markdown("<br>", unsafe_allow_html=True)
            st.success("✨ AI Analysis Complete!")
            st.info(f"🏆 **Highly Recommended Career Path:** {prediction[0]}")
            st.balloons() 

    except FileNotFoundError:
        st.error("⚠️ Model files not found! Please run `python train_model.py` in your terminal first.")

elif page == "Skill Gap Analysis":
    st.markdown(f"""
    <div style='padding-bottom: 25px;'>
        <h1 style='font-size: 2.2rem; font-weight: 800; margin-bottom: 0;'>📈 Skill Gap Analysis</h1>
        <p>Compare your current skills with industry requirements to see what you need to learn next.</p>
    </div>
    """, unsafe_allow_html=True)

    career_skills = {
        "Data Scientist": ["Python", "SQL", "Machine Learning", "Statistics", "Data Visualization"],
        "Software Engineer": ["Java", "Python", "Data Structures", "System Design", "Git"],
        "Frontend Developer": ["HTML/CSS", "JavaScript", "React", "UI/UX Design", "Git"],
        "Data Analyst": ["Excel", "SQL", "Python", "Tableau", "Statistics"],
        "Digital Marketer": ["SEO", "Content Marketing", "Google Analytics", "Social Media", "Copywriting"]
    }

    learning_resources = {
        "Python": "Python for Beginners (FreeCodeCamp - YouTube)",
        "SQL": "Intro to SQL (Kaggle)",
        "Machine Learning": "Machine Learning Specialization (Coursera)",
        "Statistics": "Statistics and Probability (Khan Academy)",
        "React": "React Crash Course (YouTube)",
        "Data Structures": "Data Structures & Algorithms (GeeksforGeeks)"
    }

    with st.container():
        st.markdown(f"<div class='custom-card'>", unsafe_allow_html=True)
        st.subheader("Your Profile")
        target_career = st.selectbox("🎯 Select your Target Career", list(career_skills.keys()))
        
        all_skills = sorted(list(set([skill for skills in career_skills.values() for skill in skills])))
        current_skills = st.multiselect("✅ Select the skills you already have", all_skills)

        analyze = st.button("Analyze My Skill Gap", type="primary", use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    if analyze:
        required_skills = set(career_skills[target_career])
        user_skills = set(current_skills)

        missing_skills = required_skills.difference(user_skills)
        matched_skills = required_skills.intersection(user_skills)
        match_percentage = int((len(matched_skills) / len(required_skills)) * 100)

        st.markdown("---")
        st.subheader("📊 Analysis Results")
        st.progress(match_percentage / 100)
        st.write(f"**Profile Match: {match_percentage}%**")

        col1, col2 = st.columns(2)
        with col1:
            st.success(f"**Skills you have ({len(matched_skills)}):**")
            for skill in matched_skills:
                st.write(f"✔️ {skill}")
        
        with col2:
            st.error(f"**Skills you need ({len(missing_skills)}):**")
            for skill in missing_skills:
                st.write(f"❌ {skill}")

        if missing_skills:
            st.markdown("---")
            st.subheader("📚 Recommended Learning Resources")
            st.info("Here are some free resources to help you bridge your skill gap:")
            for skill in missing_skills:
                resource = learning_resources.get(skill, f"Search YouTube for '{skill} full course 2024'")
                st.write(f"- **{skill}:** {resource}")
        else:
            st.balloons()
            st.success("🎉 You have all the required skills for this career! You are ready to start applying for jobs.")

elif page == "AI Chatbot":
    st.markdown(f"""
    <div style='padding-bottom: 25px;'>
        <h1 style='font-size: 2.2rem; font-weight: 800; margin-bottom: 0;'>🤖 Virtual Career Counselor</h1>
        <p>Ask me anything about careers, exams, or learning resources!</p>
    </div>
    """, unsafe_allow_html=True)

    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        model = genai.GenerativeModel('gemini-3-flash-preview')
    except Exception as e:
        st.error(f"⚠️ Please set up your .streamlit/secrets.toml file with your GEMINI_API_KEY.")
        st.stop()

    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Hi! I'm your EduBridge virtual counselor. What career or education questions can I help you with today?"}
        ]

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("E.g., How do I become a Data Scientist?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            context = f"You are a helpful, encouraging career counselor for a platform called EduBridge. Keep answers concise. User asks: {prompt}"
            with st.spinner("Thinking..."):
                response = model.generate_content(context)
                st.markdown(response.text)
        
        st.session_state.messages.append({"role": "assistant", "content": response.text})

elif page == "Admin Panel":
    st.markdown(f"""
    <div style='padding-bottom: 25px;'>
        <h1 style='font-size: 2.2rem; font-weight: 800; margin-bottom: 0;'>⚙️ Admin Panel</h1>
        <p>Manage student records, view analytics, and update platform resources.</p>
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["👥 Student Records", "📈 Platform Analytics", "📂 Manage Resources"])

    with tab1:
        st.subheader("Student Database")
        student_data = pd.DataFrame({
            "Student ID": ["EB-101", "EB-102", "EB-103", "EB-104", "EB-105"],
            "Name": ["Rahul Sharma", "Priya Patel", "Amit Singh", "Neha Gupta", "Vikram Rao"],
            "Degree": ["B.Tech CS", "BCA", "B.Sc Stats", "B.Com", "B.Tech IT"],
            "Target Career": ["Data Scientist", "Frontend Dev", "Data Analyst", "Financial Analyst", "Cloud Admin"],
            "Profile Match": ["85%", "60%", "92%", "75%", "40%"]
        })
        st.dataframe(student_data, use_container_width=True)
        st.download_button("Download CSV Report", data=student_data.to_csv(index=False).encode('utf-8'), file_name='student_records.csv', mime='text/csv')

    with tab2:
        st.subheader("Platform Usage Analytics")
        col1, col2 = st.columns(2)
        col1.metric("Total Active Students", "1,245", "+12 this week")
        col2.metric("Chatbot Queries Answered", "8,430", "+340 today")
        
        st.markdown("---")
        st.write("**Most Popular Target Careers**")
        pop_careers = pd.DataFrame({"Career": ["Data Scientist", "Software Eng.", "AI Engineer", "Data Analyst"], "Count": [450, 320, 210, 265]})
        st.bar_chart(pop_careers.set_index("Career"))

    with tab3:
        with st.form("upload_resource"):
            st.subheader("Upload New Resources")
            resource_type = st.selectbox("Resource Type", ["Free Course", "Scholarship", "YouTube Playlist", "Practice Dataset"])
            resource_name = st.text_input("Resource Title")
            resource_link = st.text_input("URL / Link")
            submit_resource = st.form_submit_button("Upload to Platform Database", use_container_width=True)
            
            if submit_resource:
                if resource_name and resource_link:
                    st.success(f"✅ Successfully added '{resource_name}'!")
                else:
                    st.error("⚠️ Please fill out all fields.")

elif page == "Student Dashboard":
    st.markdown(f"""
    <div style='padding-bottom: 25px;'>
        <h1 style='font-size: 2.2rem; font-weight: 800; margin-bottom: 0;'>📊 Student Dashboard</h1>
        <p>Welcome back! Here is an overview of your profile and learning progress.</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    col1.metric(label="Profile Completion", value="85%", delta="+5% this week")
    col2.metric(label="Top Career Match", value="Data Scientist", delta="High Alignment", delta_color="normal")
    col3.metric(label="Resources Completed", value="3", delta="+1 course", delta_color="normal")

    st.markdown("---")

    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        st.markdown("<div class='custom-card'>", unsafe_allow_html=True)
        st.subheader("Your Skill Proficiency")
        df_skills = pd.DataFrame({"Skill": ["Python", "SQL", "Machine Learning", "Statistics", "Data Viz"], "Proficiency Level (%)": [80, 75, 20, 30, 10]})
        fig_skills = px.bar(df_skills, x="Skill", y="Proficiency Level (%)", color="Skill", title="Current Skill Levels vs Target")
        fig_skills.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color=text_color))
        st.plotly_chart(fig_skills, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with chart_col2:
        st.markdown("<div class='custom-card'>", unsafe_allow_html=True)
        st.subheader("Career Interest Alignment")
        df_careers = pd.DataFrame({"Career Path": ["Data Scientist", "Data Analyst", "AI Engineer", "Software Engineer"], "Match Score": [85, 75, 60, 40]})
        fig_careers = px.pie(df_careers, names="Career Path", values="Match Score", hole=0.4, title="Recommended Paths Based on Profile")
        fig_careers.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color=text_color))
        st.plotly_chart(fig_careers, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("---")
    st.info("💡 **Tip:** Completing the *'Machine Learning Specialization'* will boost your Data Scientist match score by 20%. Head over to the **Skill Gap Analysis** tab to get the link!")