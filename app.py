#!/usr/bin/env python3
"""
Meeting Poll Web Application
A simple Flask app for creating and managing meeting polls similar to Doodle.
"""

import os
import sqlite3
import uuid
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, jsonify, g

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-in-production'

# Database configuration
DATABASE = 'polls.db'

def get_db():
    """Get database connection"""
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    """Close database connection"""
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():
    """Initialize database with required tables"""
    with app.app_context():
        db = get_db()
        db.executescript('''
            CREATE TABLE IF NOT EXISTS polls (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE TABLE IF NOT EXISTS time_slots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                poll_id TEXT NOT NULL,
                slot_datetime TEXT NOT NULL,
                FOREIGN KEY (poll_id) REFERENCES polls (id)
            );
            
            CREATE TABLE IF NOT EXISTS votes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                poll_id TEXT NOT NULL,
                voter_name TEXT NOT NULL,
                time_slot_id INTEGER NOT NULL,
                availability TEXT NOT NULL CHECK (availability IN ('yes', 'maybe', 'no')),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (poll_id) REFERENCES polls (id),
                FOREIGN KEY (time_slot_id) REFERENCES time_slots (id),
                UNIQUE(poll_id, voter_name, time_slot_id)
            );
        ''')
        db.commit()

@app.route('/')
def index():
    """Home page with create poll form"""
    return render_template('index.html')

@app.route('/create', methods=['POST'])
def create_poll():
    """Create a new poll"""
    title = request.form.get('title', '').strip()
    description = request.form.get('description', '').strip()
    time_slots = request.form.getlist('time_slots')
    
    # Filter out empty time slots
    valid_time_slots = [slot.strip() for slot in time_slots if slot.strip()]
    
    if not title or not valid_time_slots:
        return redirect(url_for('index'))
    
    # Generate unique poll ID
    poll_id = str(uuid.uuid4())[:8]
    
    db = get_db()
    
    # Insert poll
    db.execute('INSERT INTO polls (id, title, description) VALUES (?, ?, ?)',
               (poll_id, title, description))
    
    # Insert time slots (only valid ones)
    for slot in valid_time_slots:
        db.execute('INSERT INTO time_slots (poll_id, slot_datetime) VALUES (?, ?)',
                  (poll_id, slot))
    
    db.commit()
    
    return redirect(url_for('poll_detail', poll_id=poll_id))

@app.route('/poll/<poll_id>')
def poll_detail(poll_id):
    """Display poll voting page"""
    db = get_db()
    
    # Get poll info
    poll = db.execute('SELECT * FROM polls WHERE id = ?', (poll_id,)).fetchone()
    if not poll:
        return "Poll not found", 404
    
    # Get time slots - convert to dictionaries for consistency
    time_slots_raw = db.execute('SELECT * FROM time_slots WHERE poll_id = ? ORDER BY slot_datetime',
                               (poll_id,)).fetchall()
    
    time_slots = []
    for slot in time_slots_raw:
        time_slots.append({
            'id': slot['id'],
            'poll_id': slot['poll_id'], 
            'slot_datetime': slot['slot_datetime']
        })
    
    # Get all votes - convert to dictionaries for easier template access
    votes_raw = db.execute('''
        SELECT voter_name, time_slot_id, availability
        FROM votes
        WHERE poll_id = ?
        ORDER BY voter_name, time_slot_id
    ''', (poll_id,)).fetchall()
    
    # Convert votes to list of dictionaries
    votes = []
    for vote in votes_raw:
        votes.append({
            'voter_name': vote['voter_name'],
            'time_slot_id': vote['time_slot_id'], 
            'availability': vote['availability']
        })
    
    # Get unique voters
    voters_raw = db.execute('SELECT DISTINCT voter_name FROM votes WHERE poll_id = ? ORDER BY voter_name',
                           (poll_id,)).fetchall()
    
    # Convert voters to list of dictionaries
    voters = []
    for voter in voters_raw:
        voters.append({'voter_name': voter['voter_name']})
    
    # Debug: Print vote data to console for troubleshooting
    print(f"Debug - Poll ID: {poll_id}")
    print(f"Debug - Time slots: {time_slots}")
    print(f"Debug - Votes: {votes}")
    print(f"Debug - Voters: {voters}")
    
    # Test the matching logic in Python
    print("\n=== TESTING VOTE MATCHING ===")
    for voter in voters:
        print(f"Voter: {voter['voter_name']}")
        for slot in time_slots:
            print(f"  Checking slot {slot['id']}")
            matching_votes = [v for v in votes if v['voter_name'] == voter['voter_name'] and v['time_slot_id'] == slot['id']]
            if matching_votes:
                print(f"    FOUND MATCH: {matching_votes[0]}")
            else:
                print(f"    NO MATCH")
    print("=== END TEST ===\n")
    
    return render_template('poll_detail.html', 
                         poll=poll, 
                         time_slots=time_slots, 
                         votes=votes,
                         voters=voters)

@app.route('/vote', methods=['POST'])
def submit_vote():
    """Submit votes for a poll"""
    poll_id = request.form.get('poll_id')
    voter_name = request.form.get('voter_name', '').strip()
    
    if not poll_id or not voter_name:
        return redirect(url_for('index'))
    
    db = get_db()
    
    # Delete existing votes from this voter for this poll
    db.execute('DELETE FROM votes WHERE poll_id = ? AND voter_name = ?',
               (poll_id, voter_name))
    
    # Insert new votes
    for key, value in request.form.items():
        if key.startswith('slot_') and value in ['yes', 'maybe', 'no']:
            time_slot_id = key.replace('slot_', '')
            db.execute('INSERT INTO votes (poll_id, voter_name, time_slot_id, availability) VALUES (?, ?, ?, ?)',
                      (poll_id, voter_name, int(time_slot_id), value))
    
    db.commit()
    
    return redirect(url_for('poll_detail', poll_id=poll_id))

@app.route('/api/poll/<poll_id>/results')
def api_poll_results(poll_id):
    """API endpoint for poll results"""
    db = get_db()
    
    # Get time slots
    time_slots = db.execute('SELECT * FROM time_slots WHERE poll_id = ? ORDER BY slot_datetime',
                           (poll_id,)).fetchall()
    
    # Get vote counts for each time slot
    results = []
    for slot in time_slots:
        counts = db.execute('''
            SELECT availability, COUNT(*) as count
            FROM votes
            WHERE poll_id = ? AND time_slot_id = ?
            GROUP BY availability
        ''', (poll_id, slot['id'])).fetchall()
        
        count_dict = {'yes': 0, 'maybe': 0, 'no': 0}
        for count in counts:
            count_dict[count['availability']] = count['count']
        
        results.append({
            'slot_id': slot['id'],
            'slot_datetime': slot['slot_datetime'],
            'counts': count_dict
        })
    
    return jsonify(results)

# HTML Templates embedded in Python (for single-file distribution)
@app.route('/templates/<template_name>')
def serve_template(template_name):
    """Serve templates (fallback for development)"""
    return "Template not found", 404

# Create templates directory and files
def create_templates():
    """Create template files with KDC branding"""
    if not os.path.exists('templates'):
        os.makedirs('templates')
    
    # Always recreate templates to ensure latest branding
    print("🎨 Creating KDC branded templates...")
    
    # Base template
    with open('templates/base.html', 'w') as f:
        f.write('''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}KDC Meeting Scheduler{% endblock %}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        /* Kuo Diedrich Chi Brand Colors */
        :root {
            --kdc-red: #D52B1E;
            --kdc-dark-red: #B71C1C;
            --kdc-gray: #7A7A7A;
            --kdc-dark-gray: #5A5A5A;
            --kdc-light-gray: #F5F5F5;
            --kdc-white: #FFFFFF;
        }
        
        /* Navigation styling */
        .navbar-brand {
            font-weight: 700;
            font-size: 1.5rem;
            letter-spacing: 1px;
        }
        
        .navbar-brand .kdc-logo {
            background: var(--kdc-red);
            color: white;
            padding: 8px 12px;
            margin-right: 8px;
            border-radius: 4px;
            font-weight: 900;
            letter-spacing: 2px;
        }
        
        /* Voting buttons */
        .vote-btn { margin: 2px; min-width: 60px; }
        .vote-yes { background-color: var(--kdc-red); border-color: var(--kdc-red); }
        .vote-yes:hover, .vote-yes:focus { background-color: var(--kdc-dark-red); border-color: var(--kdc-dark-red); }
        .vote-maybe { background-color: #ffc107; border-color: #ffc107; color: #000; }
        .vote-no { background-color: var(--kdc-gray); border-color: var(--kdc-gray); }
        .vote-no:hover, .vote-no:focus { background-color: var(--kdc-dark-gray); border-color: var(--kdc-dark-gray); }
        
        .vote-table th { background-color: var(--kdc-light-gray); color: var(--kdc-dark-gray); }
        .time-slot-input { margin-bottom: 15px; }
        
        /* Header with brand colors */
        .poll-header { 
            background: linear-gradient(135deg, var(--kdc-red) 0%, var(--kdc-dark-red) 100%); 
            color: white; 
        }
        
        /* Primary buttons with brand color */
        .btn-primary {
            background-color: var(--kdc-red);
            border-color: var(--kdc-red);
        }
        
        .btn-primary:hover, .btn-primary:focus {
            background-color: var(--kdc-dark-red);
            border-color: var(--kdc-dark-red);
        }
        
        .btn-outline-primary {
            color: var(--kdc-red);
            border-color: var(--kdc-red);
        }
        
        .btn-outline-primary:hover, .btn-outline-primary:focus {
            background-color: var(--kdc-red);
            border-color: var(--kdc-red);
        }
        
        /* Navigation bar */
        .navbar {
            background-color: var(--kdc-red) !important;
            border-bottom: 3px solid var(--kdc-dark-red);
        }
        
        /* Enhanced date/time input styling */
        .date-input, .time-input, .end-time-input {
            border: 2px solid #e9ecef;
            border-radius: 8px;
            padding: 8px 12px;
            transition: all 0.3s ease;
        }
        
        .date-input:focus, .time-input:focus, .end-time-input:focus {
            border-color: var(--kdc-red);
            box-shadow: 0 0 0 0.2rem rgba(213, 43, 30, 0.25);
        }
        
        .time-slot-input {
            background: var(--kdc-light-gray);
            border-radius: 12px;
            padding: 15px;
            border: 1px solid #dee2e6;
            transition: all 0.3s ease;
        }
        
        .time-slot-input:hover {
            background: #e9ecef;
            border-color: var(--kdc-red);
        }
        
        /* Cards and badges */
        .card-header.bg-light {
            background-color: var(--kdc-light-gray) !important;
            border-bottom: 2px solid var(--kdc-red);
        }
        
        .badge.bg-success {
            background-color: #28a745 !important;
        }
        
        .text-success {
            color: #28a745 !important;
        }
        
        /* Calendar and time picker custom styles */
        input[type="date"]::-webkit-calendar-picker-indicator,
        input[type="time"]::-webkit-calendar-picker-indicator {
            background: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24"><path fill="%23D52B1E" d="M19 3h-1V1h-2v2H8V1H6v2H5c-1.11 0-1.99.9-1.99 2L3 19c0 1.1.89 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm0 16H5V8h14v11zM7 10h5v5H7z"/></svg>') center/contain no-repeat;
            cursor: pointer;
            padding: 4px;
        }
        
        input[type="time"]::-webkit-calendar-picker-indicator {
            background: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24"><path fill="%23D52B1E" d="M12,2A10,10 0 0,0 2,12A10,10 0 0,0 12,22A10,10 0 0,0 22,12A10,10 0 0,0 12,2M16.2,16.2L11,13V7H12.5V12.2L17,14.9L16.2,16.2Z"/></svg>') center/contain no-repeat;
        }
        
        /* Brand-colored icons */
        .fa-calendar-plus, .fa-info-circle {
            color: var(--kdc-red) !important;
        }
        
        .fa-share-alt {
            color: var(--kdc-gray) !important;
        }
        
        .fa-chart-bar {
            color: var(--kdc-dark-gray) !important;
        }
        
        /* Footer */
        footer {
            background-color: var(--kdc-light-gray) !important;
            border-top: 2px solid var(--kdc-red);
        }
        
        /* Custom shadow for cards */
        .card.shadow {
            box-shadow: 0 4px 6px -1px rgba(213, 43, 30, 0.1), 0 2px 4px -1px rgba(213, 43, 30, 0.06) !important;
        }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark">
        <div class="container">
            <a class="navbar-brand" href="{{ url_for('index') }}">
                <span class="kdc-logo">KDC</span> Meeting Scheduler
            </a>
        </div>
    </nav>
    
    <main class="container mt-4">
        {% block content %}{% endblock %}
    </main>
    
    <footer class="mt-5 py-4 text-center">
        <div class="container">
            <div class="d-flex justify-content-center align-items-center mb-2">
                <span class="kdc-logo me-2">KDC</span>
                <span class="fw-bold" style="color: var(--kdc-gray);">Kuo Diedrich Chi</span>
            </div>
            <p class="text-muted mb-0">Professional Meeting Scheduling Solutions</p>
        </div>
    </footer>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    {% block scripts %}{% endblock %}
</body>
</html>''')
    
    # Index template
    with open('templates/index.html', 'w') as f:
        f.write('''{% extends "base.html" %}

{% block title %}Create Meeting Poll{% endblock %}

{% block content %}
<div class="row justify-content-center">
    <div class="col-lg-8">
        <div class="card shadow">
            <div class="card-header poll-header text-center py-4">
                <h1 class="mb-0"><i class="fas fa-plus-circle"></i> Create a Meeting Poll</h1>
                <p class="mb-0 mt-2">Professional scheduling made simple</p>
            </div>
            <div class="card-body p-4">
                <form method="POST" action="{{ url_for('create_poll') }}" id="pollForm">
                    <div class="mb-4">
                        <label for="title" class="form-label fw-bold">
                            <i class="fas fa-heading"></i> Poll Title *
                        </label>
                        <input type="text" class="form-control form-control-lg" id="title" name="title" 
                               placeholder="e.g., Team Meeting - Sprint Planning" required>
                    </div>
                    
                    <div class="mb-4">
                        <label for="description" class="form-label fw-bold">
                            <i class="fas fa-align-left"></i> Description (Optional)
                        </label>
                        <textarea class="form-control" id="description" name="description" rows="3"
                                  placeholder="Add any additional details about the meeting..."></textarea>
                    </div>
                    
                    <div class="mb-4">
                        <label class="form-label fw-bold">
                            <i class="fas fa-clock"></i> Proposed Time Slots *
                        </label>
                        <div id="timeSlots">
                            <div class="time-slot-input">
                                <div class="row g-2">
                                    <div class="col-md-5">
                                        <label class="form-label text-muted small">Date</label>
                                        <input type="date" class="form-control date-input" required>
                                    </div>
                                    <div class="col-md-3">
                                        <label class="form-label text-muted small">Start Time</label>
                                        <input type="time" class="form-control time-input" required>
                                    </div>
                                    <div class="col-md-3">
                                        <label class="form-label text-muted small">End Time (Optional)</label>
                                        <input type="time" class="form-control end-time-input">
                                    </div>
                                    <div class="col-md-1">
                                        <label class="form-label text-muted small">&nbsp;</label>
                                        <button type="button" class="btn btn-outline-danger remove-slot d-block" style="display: none !important;">
                                            <i class="fas fa-times"></i>
                                        </button>
                                    </div>
                                </div>
                                <input type="hidden" class="formatted-slot" name="time_slots">
                            </div>
                        </div>
                        <button type="button" class="btn btn-outline-primary btn-sm mt-2" id="addSlot">
                            <i class="fas fa-plus"></i> Add Another Time Slot
                        </button>
                        <div class="form-text">
                            <i class="fas fa-info-circle"></i> Select dates and times using the calendar and time pickers above
                        </div>
                    </div>
                    
                    <div class="d-grid">
                        <button type="submit" class="btn btn-primary btn-lg">
                            <i class="fas fa-rocket"></i> Create Professional Poll
                        </button>
                    </div>
                </form>
            </div>
        </div>
        
        <div class="mt-4 text-center">
            <div class="card">
                <div class="card-body">
                    <h5><i class="fas fa-info-circle"></i> Professional Scheduling Process</h5>
                    <div class="row mt-3">
                        <div class="col-md-4">
                            <i class="fas fa-calendar-plus fa-2x mb-2"></i>
                            <p><strong>1. Schedule Options</strong><br>Select dates and times using our intuitive interface</p>
                        </div>
                        <div class="col-md-4">
                            <i class="fas fa-share-alt fa-2x mb-2"></i>
                            <p><strong>2. Share & Collaborate</strong><br>Send secure links to all participants</p>
                        </div>
                        <div class="col-md-4">
                            <i class="fas fa-chart-bar fa-2x mb-2"></i>
                            <p><strong>3. Optimize & Decide</strong><br>Make data-driven scheduling decisions</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}

{% block scripts %}
<script>
let slotCount = 1;

// Set minimum date to today
function setMinDate() {
    const today = new Date().toISOString().split('T')[0];
    document.querySelectorAll('.date-input').forEach(input => {
        input.min = today;
    });
}

// Format time slot display
function formatTimeSlot(date, startTime, endTime) {
    if (!date || !startTime) return '';
    
    const dateObj = new Date(date);
    const dayName = dateObj.toLocaleDateString('en-US', { weekday: 'long' });
    const monthDay = dateObj.toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' });
    
    // Format start time
    const [startHour, startMin] = startTime.split(':');
    const startTimeObj = new Date();
    startTimeObj.setHours(parseInt(startHour), parseInt(startMin));
    const formattedStartTime = startTimeObj.toLocaleTimeString('en-US', { 
        hour: 'numeric', 
        minute: '2-digit',
        hour12: true 
    });
    
    let timeRange = formattedStartTime;
    
    // Add end time if provided
    if (endTime) {
        const [endHour, endMin] = endTime.split(':');
        const endTimeObj = new Date();
        endTimeObj.setHours(parseInt(endHour), parseInt(endMin));
        const formattedEndTime = endTimeObj.toLocaleTimeString('en-US', { 
            hour: 'numeric', 
            minute: '2-digit',
            hour12: true 
        });
        timeRange = `${formattedStartTime} - ${formattedEndTime}`;
    }
    
    return `${dayName}, ${monthDay} at ${timeRange}`;
}

// Update hidden input with formatted time slot
function updateFormattedSlot(container) {
    const dateInput = container.querySelector('.date-input');
    const timeInput = container.querySelector('.time-input');
    const endTimeInput = container.querySelector('.end-time-input');
    const hiddenInput = container.querySelector('.formatted-slot');
    
    const formatted = formatTimeSlot(dateInput.value, timeInput.value, endTimeInput.value);
    hiddenInput.value = formatted;
}

// Add event listeners to all time slot inputs
function addTimeSlotListeners(container) {
    const inputs = container.querySelectorAll('.date-input, .time-input, .end-time-input');
    inputs.forEach(input => {
        input.addEventListener('change', () => updateFormattedSlot(container));
        input.addEventListener('input', () => updateFormattedSlot(container));
    });
}

// Add new time slot
document.getElementById('addSlot').addEventListener('click', function() {
    const slotsContainer = document.getElementById('timeSlots');
    const newSlot = document.createElement('div');
    newSlot.className = 'time-slot-input mt-3';
    newSlot.innerHTML = `
        <div class="row g-2">
            <div class="col-md-5">
                <label class="form-label text-muted small">Date</label>
                <input type="date" class="form-control date-input" required>
            </div>
            <div class="col-md-3">
                <label class="form-label text-muted small">Start Time</label>
                <input type="time" class="form-control time-input" required>
            </div>
            <div class="col-md-3">
                <label class="form-label text-muted small">End Time (Optional)</label>
                <input type="time" class="form-control end-time-input">
            </div>
            <div class="col-md-1">
                <label class="form-label text-muted small">&nbsp;</label>
                <button type="button" class="btn btn-outline-danger remove-slot d-block">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        </div>
        <input type="hidden" class="formatted-slot" name="time_slots">
    `;
    slotsContainer.appendChild(newSlot);
    slotCount++;
    setMinDate();
    addTimeSlotListeners(newSlot);
    updateRemoveButtons();
});

// Remove time slot
document.addEventListener('click', function(e) {
    if (e.target.closest('.remove-slot')) {
        e.target.closest('.time-slot-input').remove();
        slotCount--;
        updateRemoveButtons();
    }
});

// Update remove button visibility
function updateRemoveButtons() {
    const removeButtons = document.querySelectorAll('.remove-slot');
    removeButtons.forEach(button => {
        button.style.display = slotCount > 1 ? 'block' : 'none';
    });
}

// Form validation
document.getElementById('pollForm').addEventListener('submit', function(e) {
    const slots = document.querySelectorAll('.formatted-slot');
    let hasValidSlot = false;
    
    slots.forEach(slot => {
        if (slot.value.trim()) {
            hasValidSlot = true;
        }
    });
    
    if (!hasValidSlot) {
        e.preventDefault();
        alert('Please add at least one valid time slot with date and start time.');
        return false;
    }
});

// Initialize
document.addEventListener('DOMContentLoaded', function() {
    setMinDate();
    addTimeSlotListeners(document.querySelector('.time-slot-input'));
    updateRemoveButtons();
});
</script>
{% endblock %}''')
    
    # Poll detail template
    with open('templates/poll_detail.html', 'w') as f:
        f.write('''{% extends "base.html" %}

{% block title %}{{ poll.title }} - Meeting Poll{% endblock %}

{% block content %}
<div class="row">
    <div class="col-12">
        <!-- Poll Header -->
        <div class="card shadow mb-4">
            <div class="card-header poll-header text-center py-4">
                <h1 class="mb-2">{{ poll.title }}</h1>
                {% if poll.description %}
                    <p class="mb-0 lead">{{ poll.description }}</p>
                {% endif %}
                <div class="mt-3">
                    <button class="btn btn-light btn-sm" onclick="copyLink()">
                        <i class="fas fa-share"></i> Share This Poll
                    </button>
                    <span class="badge bg-light text-dark ms-2">
                        <i class="fas fa-shield-alt"></i> Secure KDC Scheduling
                    </span>
                </div>
            </div>
        </div>
        
        <!-- Voting Form -->
        <div class="card shadow mb-4">
            <div class="card-header bg-light">
                <h4 class="mb-0"><i class="fas fa-vote-yea"></i> Cast Your Vote</h4>
            </div>
            <div class="card-body">
                <form method="POST" action="{{ url_for('submit_vote') }}">
                    <input type="hidden" name="poll_id" value="{{ poll.id }}">
                    
                    <div class="mb-3">
                        <label for="voter_name" class="form-label fw-bold">Your Name *</label>
                        <input type="text" class="form-control" id="voter_name" name="voter_name" 
                               placeholder="Enter your name" required>
                    </div>
                    
                    <div class="table-responsive">
                        <table class="table table-bordered vote-table">
                            <thead>
                                <tr>
                                    <th>Time Option</th>
                                    <th class="text-center">Your Availability</th>
                                </tr>
                            </thead>
                            <tbody>
                                {% for slot in time_slots %}
                                <tr>
                                    <td class="fw-bold">{{ slot.slot_datetime }}</td>
                                    <td class="text-center">
                                        <div class="btn-group" role="group">
                                            <input type="radio" class="btn-check" name="slot_{{ slot.id }}" 
                                                   id="yes_{{ slot.id }}" value="yes">
                                            <label class="btn btn-outline-success vote-btn" for="yes_{{ slot.id }}">
                                                <i class="fas fa-check"></i> Yes
                                            </label>
                                            
                                            <input type="radio" class="btn-check" name="slot_{{ slot.id }}" 
                                                   id="maybe_{{ slot.id }}" value="maybe">
                                            <label class="btn btn-outline-warning vote-btn" for="maybe_{{ slot.id }}">
                                                <i class="fas fa-question"></i> Maybe
                                            </label>
                                            
                                            <input type="radio" class="btn-check" name="slot_{{ slot.id }}" 
                                                   id="no_{{ slot.id }}" value="no">
                                            <label class="btn btn-outline-danger vote-btn" for="no_{{ slot.id }}">
                                                <i class="fas fa-times"></i> No
                                            </label>
                                        </div>
                                    </td>
                                </tr>
                                {% endfor %}
                            </tbody>
                        </table>
                    </div>
                    
                    <div class="d-grid">
                        <button type="submit" class="btn btn-primary btn-lg">
                            <i class="fas fa-paper-plane"></i> Submit Response
                        </button>
                    </div>
                </form>
            </div>
        </div>
        
        <!-- Results Table -->
        <div class="card shadow">
            <div class="card-header bg-light">
                <h4 class="mb-0"><i class="fas fa-chart-bar"></i> Current Results</h4>
            </div>
            <div class="card-body">
                {% if voters %}
                <div class="table-responsive">
                    <table class="table table-bordered">
                        <thead>
                            <tr>
                                <th>Participant</th>
                                {% for slot in time_slots %}
                                    <th class="text-center">{{ slot.slot_datetime }}</th>
                                {% endfor %}
                            </tr>
                        </thead>
                        <tbody>
                            {% for voter in voters %}
                            <tr>
                                <td class="fw-bold">{{ voter.voter_name }}</td>
                                {% for slot in time_slots %}
                                    <td class="text-center">
                                        {% set found_vote = false %}
                                        {% for vote in votes %}
                                            {% if not found_vote and vote.voter_name == voter.voter_name and vote.time_slot_id == slot.id %}
                                                {% set found_vote = true %}
                                                {% if vote.availability == 'yes' %}
                                                    <span class="badge bg-success"><i class="fas fa-check"></i> Yes</span>
                                                {% elif vote.availability == 'maybe' %}
                                                    <span class="badge bg-warning text-dark"><i class="fas fa-question"></i> Maybe</span>
                                                {% elif vote.availability == 'no' %}
                                                    <span class="badge bg-danger"><i class="fas fa-times"></i> No</span>
                                                {% else %}
                                                    <span class="text-muted">UNKNOWN: {{ vote.availability }}</span>
                                                {% endif %}
                                            {% endif %}
                                        {% endfor %}
                                        {% if not found_vote %}
                                            <span class="text-muted">-</span>
                                        {% endif %}
                                    </td>
                                {% endfor %}
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
                
                <!-- Summary Row -->
                <div class="mt-4">
                    <h5>Summary</h5>
                    <div class="table-responsive">
                        <table class="table table-sm">
                            <thead>
                                <tr>
                                    <th>Time Option</th>
                                    <th class="text-center text-success">Yes</th>
                                    <th class="text-center text-warning">Maybe</th>
                                    <th class="text-center text-danger">No</th>
                                    <th class="text-center">Total</th>
                                </tr>
                            </thead>
                            <tbody>
                                {% for slot in time_slots %}
                                <tr>
                                    <td class="fw-bold">{{ slot.slot_datetime }}</td>
                                    {% set yes_count = votes | selectattr('time_slot_id', 'equalto', slot.id) | selectattr('availability', 'equalto', 'yes') | list | length %}
                                    {% set maybe_count = votes | selectattr('time_slot_id', 'equalto', slot.id) | selectattr('availability', 'equalto', 'maybe') | list | length %}
                                    {% set no_count = votes | selectattr('time_slot_id', 'equalto', slot.id) | selectattr('availability', 'equalto', 'no') | list | length %}
                                    <td class="text-center">
                                        <span class="badge bg-success">{{ yes_count }}</span>
                                    </td>
                                    <td class="text-center">
                                        <span class="badge bg-warning text-dark">{{ maybe_count }}</span>
                                    </td>
                                    <td class="text-center">
                                        <span class="badge bg-danger">{{ no_count }}</span>
                                    </td>
                                    <td class="text-center fw-bold">{{ yes_count + maybe_count + no_count }}</td>
                                </tr>
                                {% endfor %}
                            </tbody>
                        </table>
                    </div>
                </div>
                {% else %}
                <div class="text-center py-4">
                    <i class="fas fa-inbox fa-3x text-muted mb-3"></i>
                    <h5 class="text-muted">No votes yet</h5>
                    <p class="text-muted">Be the first to vote on this poll!</p>
                </div>
                {% endif %}
            </div>
        </div>
    </div>
</div>
{% endblock %}

{% block scripts %}
<script>
function copyLink() {
    const url = window.location.href;
    
    if (navigator.clipboard) {
        navigator.clipboard.writeText(url).then(function() {
            showNotification('Link copied to clipboard!', 'success');
        });
    } else {
        // Fallback for older browsers
        const textArea = document.createElement('textarea');
        textArea.value = url;
        document.body.appendChild(textArea);
        textArea.select();
        document.execCommand('copy');
        document.body.removeChild(textArea);
        showNotification('Link copied to clipboard!', 'success');
    }
}

function showNotification(message, type) {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    alertDiv.style.cssText = 'top: 20px; right: 20px; z-index: 1050; min-width: 300px;';
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    document.body.appendChild(alertDiv);
    
    setTimeout(() => {
        if (alertDiv.parentNode) {
            alertDiv.parentNode.removeChild(alertDiv);
        }
    }, 3000);
}

// Auto-refresh results every 30 seconds
setInterval(function() {
    location.reload();
}, 30000);
</script>
{% endblock %}''')

if __name__ == '__main__':
    # Get port from environment variable for production
    port = int(os.environ.get('PORT', 5000))
    
    # Force recreate templates with KDC branding
    if os.path.exists('templates'):
        import shutil
        shutil.rmtree('templates')
        print("🔄 Removing old templates...")
    
    # Create templates with new branding
    create_templates()
    
    # Initialize database
    init_db()
    
    print("🚀 KDC Meeting Scheduler Starting...")
    print("🎨 KDC branded templates created")
    print("📊 Database initialized")
    print(f"🌐 Server starting on port {port}")
    print("💡 Press Ctrl+C to stop the server")
    
    # Run the app - different settings for production vs development
    if os.environ.get('RENDER'):
        # Production settings for Render
        app.run(host='0.0.0.0', port=port, debug=False)
    else:
        # Development settings
        app.run(debug=True, host='0.0.0.0', port=port)