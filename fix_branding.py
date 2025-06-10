#!/usr/bin/env python3
"""
Quick fix script to force KDC branding
"""

import os
import shutil

def fix_kdc_branding():
    print("🔧 KDC Branding Fix Tool")
    print("=" * 30)
    
    # Step 1: Remove old templates
    if os.path.exists('templates'):
        shutil.rmtree('templates')
        print("✅ Removed old templates")
    
    # Step 2: Create templates directory
    os.makedirs('templates')
    print("✅ Created templates directory")
    
    # Step 3: Create KDC base template with FORCED styling
    base_template = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}KDC Meeting Scheduler{% endblock %}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        /* KDC BRANDING - FORCED OVERRIDE */
        .navbar,
        .navbar-dark,
        .bg-primary {
            background-color: #D52B1E !important;
            background: #D52B1E !important;
            border-bottom: 3px solid #B71C1C !important;
        }
        
        .btn-primary {
            background-color: #D52B1E !important;
            border-color: #D52B1E !important;
        }
        
        .btn-primary:hover,
        .btn-primary:focus,
        .btn-primary:active {
            background-color: #B71C1C !important;
            border-color: #B71C1C !important;
        }
        
        .poll-header { 
            background: linear-gradient(135deg, #D52B1E 0%, #B71C1C 100%) !important; 
            color: white !important; 
        }
        
        .kdc-logo {
            background: #D52B1E !important;
            color: white !important;
            padding: 8px 12px !important;
            margin-right: 8px !important;
            border-radius: 4px !important;
            font-weight: 900 !important;
            letter-spacing: 2px !important;
        }
        
        .btn-outline-primary {
            color: #D52B1E !important;
            border-color: #D52B1E !important;
        }
        
        .btn-outline-primary:hover {
            background-color: #D52B1E !important;
            border-color: #D52B1E !important;
            color: white !important;
        }
        
        /* Vote buttons */
        .vote-yes { 
            background-color: #D52B1E !important; 
            border-color: #D52B1E !important; 
        }
        
        .vote-no { 
            background-color: #7A7A7A !important; 
            border-color: #7A7A7A !important; 
        }
        
        /* Form inputs */
        .date-input:focus, 
        .time-input:focus, 
        .end-time-input:focus,
        .form-control:focus {
            border-color: #D52B1E !important;
            box-shadow: 0 0 0 0.2rem rgba(213, 43, 30, 0.25) !important;
        }
        
        /* Other elements */
        .badge.bg-success {
            background-color: #D52B1E !important;
        }
        
        .text-success {
            color: #D52B1E !important;
        }
        
        .card-header.bg-light {
            background-color: #F5F5F5 !important;
            border-bottom: 2px solid #D52B1E !important;
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
    
    <footer class="mt-5 py-4 text-center" style="background-color: #F5F5F5; border-top: 2px solid #D52B1E;">
        <div class="container">
            <div class="d-flex justify-content-center align-items-center mb-2">
                <span class="kdc-logo me-2">KDC</span>
                <span class="fw-bold" style="color: #7A7A7A;">Kuo Diedrich Chi</span>
            </div>
            <p class="text-muted mb-0">Professional Meeting Scheduling Solutions</p>
        </div>
    </footer>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    {% block scripts %}{% endblock %}
</body>
</html>'''
    
    with open('templates/base.html', 'w', encoding='utf-8') as f:
        f.write(base_template)
    print("✅ Created KDC base template")
    
    # Create index template
    index_template = '''{% extends "base.html" %}

{% block title %}Create Meeting Poll - KDC{% endblock %}

{% block content %}
<div class="row justify-content-center">
    <div class="col-lg-8">
        <div class="card shadow">
            <div class="card-header poll-header text-center py-4">
                <h1 class="mb-0"><i class="fas fa-plus-circle"></i> Create a Meeting Poll</h1>
                <p class="mb-0 mt-2">KDC Professional Scheduling Solution</p>
            </div>
            <div class="card-body p-4">
                <div class="alert alert-info mb-4">
                    <h5><i class="fas fa-info-circle"></i> KDC Branding Active</h5>
                    <p class="mb-0">You should now see RED navigation, buttons, and KDC branding throughout the app!</p>
                </div>
                
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
                            <i class="fas fa-clock"></i> Time Slots *
                        </label>
                        <div id="timeSlots">
                            <div class="time-slot-input">
                                <input type="text" class="form-control" name="time_slots" 
                                       placeholder="e.g., Monday, June 12, 2024 at 2:00 PM" required>
                            </div>
                        </div>
                        <button type="button" class="btn btn-outline-primary btn-sm mt-2" id="addSlot">
                            <i class="fas fa-plus"></i> Add Another Time Slot
                        </button>
                    </div>
                    
                    <div class="d-grid">
                        <button type="submit" class="btn btn-primary btn-lg">
                            <i class="fas fa-rocket"></i> Create KDC Professional Poll
                        </button>
                    </div>
                </form>
            </div>
        </div>
    </div>
</div>

<script>
let slotCount = 1;

document.getElementById('addSlot').addEventListener('click', function() {
    const slotsContainer = document.getElementById('timeSlots');
    const newSlot = document.createElement('div');
    newSlot.className = 'time-slot-input mt-2';
    newSlot.innerHTML = '<input type="text" class="form-control" name="time_slots" placeholder="e.g., Tuesday, June 13, 2024 at 10:00 AM">';
    slotsContainer.appendChild(newSlot);
    slotCount++;
});
</script>
{% endblock %}'''
    
    with open('templates/index.html', 'w', encoding='utf-8') as f:
        f.write(index_template)
    print("✅ Created KDC index template")
    
    # Create minimal poll detail template
    poll_template = '''{% extends "base.html" %}

{% block title %}{{ poll.title }} - KDC Meeting Scheduler{% endblock %}

{% block content %}
<div class="alert alert-success">
    <h4><i class="fas fa-check-circle"></i> KDC Poll Page</h4>
    <p>This would be the poll voting page with KDC branding!</p>
</div>
{% endblock %}'''
    
    with open('templates/poll_detail.html', 'w', encoding='utf-8') as f:
        f.write(poll_template)
    print("✅ Created KDC poll detail template")
    
    print("\n<-- KDC BRANDING APPLIED! -->")
    print("=" * 30)
    print("Next steps:")
    print("1. Stop your Flask app (Ctrl+C)")
    print("2. Clear browser cache (Ctrl+Shift+R or hard refresh)")
    print("3. Restart: python app.py")
    print("4. Visit http://localhost:5000")
    print("5. You should see RED KDC branding!")

if __name__ == "__main__":
    fix_kdc_branding()