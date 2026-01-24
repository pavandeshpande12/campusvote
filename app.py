"""
CampusVote - Student Council Elections 2026
A beautiful, minimal voting app with real-time results
Vote -> Results - That's it!
"""

import streamlit as st
import plotly.graph_objects as go
from database import init_db, get_db, close_db
from models import Candidate, Vote
import re
import html

# ============================================================
# CONFIGURATION
# ============================================================

# Pre-seeded candidates data
DEFAULT_CANDIDATES = [
    {
        "name": "Arjun Mehta",
        "position": "President",
        "description": "Experienced leader with 3 years on student council. Focused on improving campus facilities, extending library hours, and creating more student job opportunities.",
        "photo": "arjun.jpg"
    },
    {
        "name": "Priya Sharma",
        "position": "President",
        "description": "Passionate about student wellness and sustainability. Plans include mental health resources, eco-friendly initiatives, and better food options on campus.",
        "photo": "priya.jpg"
    },
    {
        "name": "Rahul Nair",
        "position": "President",
        "description": "Tech-savvy innovator pushing for digital transformation. Proposes a student app, online voting for all decisions, and free software licenses for students.",
        "photo": "rahul.jpg"
    }
]

# Demo votes to make results look realistic
DEMO_VOTES = [
    ("student1@campus.edu", 1),
    ("student2@campus.edu", 1),
    ("student3@campus.edu", 2),
    ("student4@campus.edu", 1),
    ("student5@campus.edu", 3),
    ("student6@campus.edu", 2),
    ("student7@campus.edu", 1),
    ("student8@campus.edu", 2),
    ("student9@campus.edu", 3),
    ("student10@campus.edu", 1),
]

# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="CampusVote - Student Council Elections",
    page_icon="",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ============================================================
# CUSTOM CSS STYLING
# ============================================================

st.markdown("""
<style>
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Main container styling */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1200px;
    }

    /* Card styling */
    .candidate-card {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        border-radius: 16px;
        padding: 24px;
        margin: 12px 0;
        border: 1px solid #4F46E5;
        transition: all 0.3s ease;
        box-shadow: 0 4px 20px rgba(79, 70, 229, 0.15);
    }

    .candidate-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 30px rgba(79, 70, 229, 0.25);
        border-color: #6366f1;
    }

    .candidate-name {
        font-size: 1.5rem;
        font-weight: 700;
        color: #FAFAFA;
        margin-bottom: 4px;
    }

    .candidate-position {
        font-size: 0.9rem;
        color: #4F46E5;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 12px;
    }

    .candidate-description {
        color: #A0A0A0;
        font-size: 0.95rem;
        line-height: 1.6;
    }

    /* Welcome section */
    .welcome-container {
        text-align: center;
        padding: 60px 20px;
    }

    .welcome-title {
        font-size: 3rem;
        font-weight: 800;
        background: linear-gradient(135deg, #4F46E5 0%, #7C3AED 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 8px;
    }

    .welcome-subtitle {
        font-size: 1.3rem;
        color: #A0A0A0;
        margin-bottom: 40px;
    }

    /* Trust badges */
    .trust-badges {
        display: flex;
        justify-content: center;
        gap: 30px;
        margin-top: 30px;
        flex-wrap: wrap;
    }

    .trust-badge {
        color: #4F46E5;
        font-size: 0.9rem;
        font-weight: 500;
    }

    /* Results styling */
    .result-card {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        border-radius: 12px;
        padding: 16px 20px;
        margin: 8px 0;
        border-left: 4px solid #4F46E5;
    }

    .result-name {
        font-size: 1.1rem;
        font-weight: 600;
        color: #FAFAFA;
    }

    .result-votes {
        color: #4F46E5;
        font-weight: 700;
    }

    /* Progress bar animation */
    .progress-bar {
        height: 24px;
        border-radius: 12px;
        background: linear-gradient(90deg, #4F46E5 0%, #7C3AED 100%);
        transition: width 0.8s ease-out;
    }

    /* Thank you section */
    .thank-you {
        text-align: center;
        padding: 60px 20px;
        background: linear-gradient(135deg, rgba(79, 70, 229, 0.1) 0%, rgba(124, 58, 237, 0.1) 100%);
        border-radius: 20px;
        margin: 20px 0;
    }

    /* Stats cards */
    .stat-card {
        background: #262730;
        border-radius: 12px;
        padding: 20px;
        text-align: center;
    }

    .stat-number {
        font-size: 2.5rem;
        font-weight: 800;
        color: #4F46E5;
    }

    .stat-label {
        color: #A0A0A0;
        font-size: 0.9rem;
    }

    /* Candidate photo placeholder */
    .photo-placeholder {
        width: 120px;
        height: 120px;
        border-radius: 50%;
        background: linear-gradient(135deg, #4F46E5 0%, #7C3AED 100%);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 3rem;
        margin: 0 auto 16px auto;
    }

    /* Navigation buttons */
    .nav-button {
        background: transparent;
        border: 2px solid #4F46E5;
        color: #4F46E5;
        padding: 10px 24px;
        border-radius: 8px;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s ease;
    }

    .nav-button:hover {
        background: #4F46E5;
        color: #FAFAFA;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================
# DATABASE FUNCTIONS
# ============================================================

def seed_candidates():
    """Seed default candidates if none exist"""
    db = get_db()
    try:
        count = db.query(Candidate).count()
        if count == 0:
            for c in DEFAULT_CANDIDATES:
                candidate = Candidate(
                    name=c["name"],
                    position=c["position"],
                    description=c["description"],
                    photo=c["photo"],
                    vote_count=0
                )
                db.add(candidate)
            db.commit()
    except Exception:
        db.rollback()
    finally:
        close_db(db)


def seed_demo_votes():
    """Seed demo votes for realistic results"""
    db = get_db()
    try:
        vote_count = db.query(Vote).count()
        if vote_count == 0:
            for email, candidate_id in DEMO_VOTES:
                vote = Vote(voter_email=email, candidate_id=candidate_id)
                db.add(vote)
                candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
                if candidate:
                    candidate.vote_count += 1
            db.commit()
    except Exception:
        db.rollback()
    finally:
        close_db(db)


def get_candidates():
    """Get all candidates"""
    db = get_db()
    try:
        candidates = db.query(Candidate).all()
        return [{"id": c.id, "name": c.name, "position": c.position,
                 "description": c.description, "photo": c.photo,
                 "vote_count": c.vote_count} for c in candidates]
    finally:
        close_db(db)


def has_voted(email):
    """Check if email has already voted"""
    db = get_db()
    try:
        clean_email = email.lower().strip()[:100]
        vote = db.query(Vote).filter(Vote.voter_email == clean_email).first()
        return vote is not None
    finally:
        close_db(db)


def cast_vote(email, candidate_id):
    """Cast a vote for a candidate"""
    db = get_db()
    try:
        # Sanitize email
        clean_email = email.lower().strip()[:100]

        # Verify candidate exists
        candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
        if not candidate:
            return False, "Invalid candidate selected."

        # Check if already voted (double-check in same transaction)
        existing_vote = db.query(Vote).filter(Vote.voter_email == clean_email).first()
        if existing_vote:
            return False, "You have already voted!"

        # Create vote
        vote = Vote(voter_email=clean_email, candidate_id=candidate_id)
        db.add(vote)

        # Update candidate vote count
        candidate.vote_count += 1

        db.commit()
        return True, "Vote cast successfully!"
    except Exception:
        db.rollback()
        return False, "An error occurred while casting your vote. Please try again."
    finally:
        close_db(db)


def get_total_votes():
    """Get total number of votes"""
    db = get_db()
    try:
        return db.query(Vote).count()
    finally:
        close_db(db)


def validate_email(email):
    """Validate email format and length"""
    if not email or len(email) > 100:
        return False
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

# ============================================================
# INITIALIZE APP
# ============================================================

# Initialize database
init_db()
seed_candidates()
seed_demo_votes()

# Initialize session state
if "voter_email" not in st.session_state:
    st.session_state.voter_email = None
if "has_voted" not in st.session_state:
    st.session_state.has_voted = False
if "view" not in st.session_state:
    st.session_state.view = "welcome"
if "just_voted" not in st.session_state:
    st.session_state.just_voted = False
if "voted_candidate" not in st.session_state:
    st.session_state.voted_candidate = None

# ============================================================
# VIEW FUNCTIONS
# ============================================================

def show_welcome():
    """Welcome screen with email input"""
    st.markdown("""
    <div class="welcome-container">
        <div class="welcome-title">CampusVote</div>
        <div class="welcome-subtitle">Student Council Elections 2026</div>
    </div>
    """, unsafe_allow_html=True)

    # Centered email input
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("### Enter your email to vote")
        email = st.text_input("Email Address", placeholder="your.email@campus.edu",
                             label_visibility="collapsed", key="email_input")

        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("Continue to Vote", type="primary", use_container_width=True):
                if not email:
                    st.error("Please enter your email address")
                elif not validate_email(email):
                    st.error("Please enter a valid email address")
                else:
                    st.session_state.voter_email = email.lower()
                    if has_voted(email):
                        st.session_state.has_voted = True
                        st.warning("You have already voted. Redirecting to results...")
                        st.session_state.view = "results"
                    else:
                        st.session_state.view = "vote"
                    st.rerun()

        with col_b:
            if st.button("View Results", use_container_width=True):
                st.session_state.view = "results"
                st.rerun()

    # Trust badges
    st.markdown("""
    <div class="trust-badges">
        <span class="trust-badge">Anonymous Voting</span>
        <span class="trust-badge">Secure & Encrypted</span>
        <span class="trust-badge">One Vote Per Person</span>
    </div>
    """, unsafe_allow_html=True)

    # How it works
    st.markdown("---")
    st.markdown("### How It Works")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        **1. Enter Email**
        Simply enter your campus email to get started
        """)
    with col2:
        st.markdown("""
        **2. Choose Candidate**
        Review candidates and cast your vote
        """)
    with col3:
        st.markdown("""
        **3. View Results**
        See live election results instantly
        """)


def show_voting():
    """Voting screen with candidate cards"""
    # Header with navigation
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("## Choose Your Candidate")
        if st.session_state.voter_email:
            st.caption(f"Voting as: {st.session_state.voter_email}")
    with col2:
        if st.button("View Results", key="results_btn"):
            st.session_state.view = "results"
            st.rerun()

    st.markdown("---")

    # Get candidates
    candidates = get_candidates()

    if not candidates:
        st.warning("No candidates available")
        return

    # Display candidate cards
    cols = st.columns(len(candidates))

    for i, candidate in enumerate(candidates):
        with cols[i]:
            # Get initials for avatar (escaped for safety)
            safe_name = html.escape(candidate["name"])
            safe_position = html.escape(candidate["position"])
            safe_description = html.escape(candidate["description"] or "")
            initials = "".join([name[0] for name in candidate["name"].split()[:2]])

            st.markdown(f"""
            <div class="candidate-card">
                <div class="photo-placeholder">{html.escape(initials)}</div>
                <div class="candidate-name">{safe_name}</div>
                <div class="candidate-position">{safe_position}</div>
                <div class="candidate-description">{safe_description}</div>
            </div>
            """, unsafe_allow_html=True)

            # Expandable agenda section
            with st.expander("View Full Agenda"):
                st.write(candidate["description"])
                st.markdown("**Key Priorities:**")
                # Generate some bullet points from description
                points = candidate["description"].split(". ")
                for point in points[:3]:
                    if point.strip():
                        st.markdown(f"- {point.strip()}")

            # Vote button
            if st.button(f"Vote for {candidate['name'].split()[0]}",
                        key=f"vote_{candidate['id']}",
                        type="primary",
                        use_container_width=True):
                if not st.session_state.voter_email:
                    st.error("Please enter your email first")
                    st.session_state.view = "welcome"
                    st.rerun()
                else:
                    success, message = cast_vote(st.session_state.voter_email, candidate["id"])
                    if success:
                        st.session_state.has_voted = True
                        st.session_state.just_voted = True
                        st.session_state.voted_candidate = candidate["name"]
                        st.session_state.view = "thank_you"
                        st.rerun()
                    else:
                        st.error(message)

    # Back button
    st.markdown("---")
    if st.button("Back to Welcome"):
        st.session_state.view = "welcome"
        st.rerun()


def show_thank_you():
    """Thank you screen after voting"""
    safe_candidate = html.escape(st.session_state.voted_candidate or "your candidate")
    st.markdown(f"""
    <div class="thank-you">
        <h1 style="font-size: 4rem; margin-bottom: 20px;">Thank You!</h1>
        <p style="font-size: 1.3rem; color: #A0A0A0; margin-bottom: 10px;">
            Your vote has been recorded successfully.
        </p>
        <p style="font-size: 1.1rem; color: #4F46E5; font-weight: 600;">
            You voted for {safe_candidate}
        </p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("View Live Results", type="primary", use_container_width=True):
            st.session_state.just_voted = False
            st.session_state.view = "results"
            st.rerun()

        st.markdown("")

        if st.button("Back to Home", use_container_width=True):
            st.session_state.view = "welcome"
            st.rerun()


def show_results():
    """Results screen with charts and stats"""
    # Header
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("## Live Results")
    with col2:
        if st.button("Back to Vote", key="back_vote"):
            st.session_state.view = "vote" if st.session_state.voter_email else "welcome"
            st.rerun()

    # Stats row
    candidates = get_candidates()
    total_votes = get_total_votes()

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Votes Cast", total_votes)
    with col2:
        st.metric("Candidates", len(candidates))
    with col3:
        leader = max(candidates, key=lambda x: x["vote_count"]) if candidates else None
        st.metric("Current Leader", leader["name"] if leader else "N/A")

    st.markdown("---")

    if not candidates:
        st.warning("No results available yet")
        return

    # Sort candidates by votes
    sorted_candidates = sorted(candidates, key=lambda x: x["vote_count"], reverse=True)

    # Charts row
    col1, col2 = st.columns(2)

    with col1:
        # Bar chart
        fig_bar = go.Figure(data=[
            go.Bar(
                x=[c["name"] for c in sorted_candidates],
                y=[c["vote_count"] for c in sorted_candidates],
                marker_color=['#4F46E5', '#7C3AED', '#A78BFA'],
                text=[c["vote_count"] for c in sorted_candidates],
                textposition='outside'
            )
        ])
        fig_bar.update_layout(
            title="Votes by Candidate",
            xaxis_title="",
            yaxis_title="Votes",
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#FAFAFA'),
            height=350
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    with col2:
        # Pie chart
        if total_votes > 0:
            fig_pie = go.Figure(data=[
                go.Pie(
                    labels=[c["name"] for c in sorted_candidates],
                    values=[c["vote_count"] for c in sorted_candidates],
                    hole=0.4,
                    marker_colors=['#4F46E5', '#7C3AED', '#A78BFA'],
                    textinfo='percent+label',
                    textposition='outside'
                )
            ])
            fig_pie.update_layout(
                title="Vote Distribution",
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#FAFAFA'),
                height=350,
                showlegend=False
            )
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.info("Vote distribution will appear once votes are cast")

    # Detailed results
    st.markdown("### Detailed Results")

    medals = ["1st", "2nd", "3rd"]

    for i, candidate in enumerate(sorted_candidates):
        percentage = (candidate["vote_count"] / total_votes * 100) if total_votes > 0 else 0

        col1, col2, col3 = st.columns([1, 3, 1])

        with col1:
            rank = medals[i] if i < 3 else f"{i+1}th"
            st.markdown(f"### {rank}")

        with col2:
            st.markdown(f"**{candidate['name']}** - {candidate['position']}")
            st.progress(percentage / 100 if percentage > 0 else 0)

        with col3:
            st.markdown(f"**{candidate['vote_count']}** votes")
            st.caption(f"{percentage:.1f}%")

    # Refresh button
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("Refresh Results", use_container_width=True):
            st.rerun()


# ============================================================
# MAIN APP ROUTING
# ============================================================

def main():
    """Main app entry point"""
    # Route to appropriate view
    if st.session_state.view == "welcome":
        show_welcome()
    elif st.session_state.view == "vote":
        show_voting()
    elif st.session_state.view == "thank_you":
        show_thank_you()
    elif st.session_state.view == "results":
        show_results()
    else:
        show_welcome()

    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666; padding: 20px 0;'>
        <p style='margin: 5px 0;'>Designed & Developed by <strong>Pavan Deshpande</strong></p>
        <p style='margin: 5px 0; font-size: 0.8rem;'>CampusVote 2026. All rights reserved.</p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
